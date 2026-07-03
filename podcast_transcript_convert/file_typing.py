from collections.abc import Iterable
from enum import StrEnum, auto

from podcast_transcript_convert.file_utils import (
    _read_first_line,
    map_files_in_parallel,
)


class FileType(StrEnum):
    HTML = auto()
    JSON = auto()
    SRT = auto()
    VTT = auto()
    XML = auto()
    UNKNOWN = auto()


_extension_to_type = {
    "vtt": FileType.VTT,
    "srt": FileType.SRT,
    "htm": FileType.HTML,
    "html": FileType.HTML,
    "json": FileType.JSON,
    "xml": FileType.XML,
    "xsl": FileType.XML,
}


def _extract_file_type_from_name(file_path: str) -> FileType:
    extension = file_path.rsplit(".", maxsplit=1)[-1].lower()
    return _extension_to_type.get(extension, FileType.UNKNOWN)


def _extract_file_type_from_first_line(line: str) -> FileType:
    stripped = line.strip()
    if not stripped:
        return FileType.UNKNOWN
    if "WEBVTT" in line:
        return FileType.VTT
    if stripped[0] == "1" or "-->" in line:
        return FileType.SRT
    if stripped.startswith("<?xml") or "podlove.org/simple-transcripts" in line:
        return FileType.XML
    if "<" in line:
        return FileType.HTML
    return FileType.JSON if "{" in line and "rtf" not in line else FileType.UNKNOWN


def _extract_file_type_from_content(file_path: str) -> FileType:
    try:
        first_line = _read_first_line(file_path)
    except OSError:
        return FileType.UNKNOWN
    return _extract_file_type_from_first_line(first_line)


def identify_file_type(file_path: str) -> FileType:
    if (file_type := _extract_file_type_from_name(file_path)) != FileType.UNKNOWN:
        return file_type
    return _extract_file_type_from_content(file_path)


def identify_file_types(file_paths: Iterable[str]) -> dict[FileType, list[str]]:
    """Group file paths by detected transcript type.

    Files whose extension is not recognized get their first line inspected
    (in parallel). Returns a dict with an entry for every FileType; files
    that cannot be identified end up under FileType.UNKNOWN.
    """
    grouped: dict[FileType, list[str]] = {file_type: [] for file_type in FileType}
    for file_path in file_paths:
        grouped[_extract_file_type_from_name(file_path)].append(file_path)

    # Inspect first lines of unknown-extension files and reassign any matches
    types_from_content = map_files_in_parallel(
        file_paths=grouped[FileType.UNKNOWN],
        transform=_extract_file_type_from_content,
    )
    grouped[FileType.UNKNOWN] = []
    for file_path, found_type in types_from_content:
        grouped[found_type].append(file_path)

    return grouped

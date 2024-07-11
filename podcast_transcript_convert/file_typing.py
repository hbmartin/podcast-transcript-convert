from collections.abc import Iterable
from enum import StrEnum, auto
from typing import NamedTuple

from podcast_transcript_convert.file_utils import (
    _read_files_in_parallel,
    _read_first_line,
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


class TypedFileLists(NamedTuple):
    """html_files, json_files, srt_files, vtt_files, xml_files, unknown_files."""

    html_files: list[str]
    json_files: list[str]
    srt_files: list[str]
    vtt_files: list[str]
    xml_files: list[str]
    unknown_files: list[str]


def _extract_file_type_from_name(file_path: str) -> FileType:
    extension = file_path.split(".")[-1]
    return _extension_to_type.get(extension, FileType.UNKNOWN)


def _extract_file_type_from_first_line(line: str) -> FileType:
    if "WEBVTT" in line:
        return FileType.VTT
    if line[0] == "1" or "-->" in line:
        return FileType.SRT
    if "<" in line:
        return FileType.HTML
    if "{" in line and "rtf" not in line:
        return FileType.JSON
    return FileType.UNKNOWN


def _extract_file_types_from_name(
    file_paths: Iterable[str],
) -> TypedFileLists:
    srt_files = []
    vtt_files = []
    html_files = []
    json_files = []
    xml_files = []
    unknown_files = []

    for file_path in file_paths:
        match _extract_file_type_from_name(file_path):
            case FileType.VTT:
                vtt_files.append(file_path)
            case FileType.SRT:
                srt_files.append(file_path)
            case FileType.HTML:
                html_files.append(file_path)
            case FileType.JSON:
                json_files.append(file_path)
            case FileType.XML:
                xml_files.append(file_path)
            case FileType.UNKNOWN:
                unknown_files.append(file_path)

    return TypedFileLists(
        html_files,
        json_files,
        srt_files,
        vtt_files,
        xml_files,
        unknown_files,
    )


def identify_file_type(file_path: str) -> FileType:
    if (file_type := _extract_file_type_from_name(file_path)) != FileType.UNKNOWN:
        return file_type
    return _extract_file_type_from_first_line(_read_first_line(file_path))


def identify_file_types(file_paths: Iterable[str]) -> TypedFileLists:
    (
        html_files,
        json_files,
        srt_files,
        vtt_files,
        xml_files,
        unknown_files,
    ) = _extract_file_types_from_name(
        file_paths,
    )
    # Enumerate first_lines and indentify any files matching patterns
    types_from_firstline = _read_files_in_parallel(
        file_paths=unknown_files,
        transform=_extract_file_type_from_first_line,
    )
    for file_name, found_type in enumerate(types_from_firstline):
        match found_type:
            case FileType.VTT:
                vtt_files.append(file_name)
            case FileType.SRT:
                srt_files.append(file_name)
            case FileType.HTML:
                html_files.append(file_name)
            case FileType.JSON:
                json_files.append(file_name)
            case FileType.XML:
                xml_files.append(file_name)

    known_files = vtt_files + srt_files + html_files + json_files
    unknown_pods = [
        file_name for file_name in unknown_files if file_name not in known_files
    ]
    return TypedFileLists(
        html_files,
        json_files,
        srt_files,
        vtt_files,
        xml_files,
        unknown_pods,
    )

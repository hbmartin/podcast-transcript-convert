from pathlib import Path

from podcast_transcript_convert.converters import FILE_CONVERTERS, Converter
from podcast_transcript_convert.errors import UnknownFileTypeError
from podcast_transcript_convert.file_typing import FileType, identify_file_type

# Deprecated alias kept for backwards compatibility; use FILE_CONVERTERS.
type_to_converter_map: dict[FileType, Converter] = FILE_CONVERTERS


def transcript_file_to_simple_file(
    origin_file: str | Path,
    destination_file: str | Path,
    metadata: dict | None = None,
) -> None:
    file_type = identify_file_type(str(origin_file))
    if file_type == FileType.UNKNOWN:
        raise UnknownFileTypeError(str(origin_file))

    converter = FILE_CONVERTERS[file_type]
    converter(origin_file, destination_file, metadata)

from collections.abc import Callable
from pathlib import Path
from typing import TypeAlias

from podcast_transcript_convert.converters.html_to_json import html_file_to_json_file
from podcast_transcript_convert.converters.json_to_json import json_file_to_json_file
from podcast_transcript_convert.converters.srt_to_json import srt_file_to_json_file
from podcast_transcript_convert.converters.vtt_to_json import vtt_file_to_json_file
from podcast_transcript_convert.converters.xml_to_json import xml_file_to_json_file
from podcast_transcript_convert.errors import UnknownFileTypeError
from podcast_transcript_convert.file_typing import FileType, identify_file_type

Converter: TypeAlias = Callable[[str | Path, str | Path, dict | None], None]

type_to_converter_map: dict[FileType, Converter] = {
    FileType.HTML: html_file_to_json_file,
    FileType.JSON: json_file_to_json_file,
    FileType.SRT: srt_file_to_json_file,
    FileType.VTT: vtt_file_to_json_file,
    FileType.XML: xml_file_to_json_file,
}


def transcript_file_to_simple_file(
    origin_file: str | Path,
    destination_file: str | Path,
    metadata: dict | None = None,
) -> None:
    file_type = identify_file_type(origin_file)
    if file_type == FileType.UNKNOWN:
        raise UnknownFileTypeError(origin_file)

    converter = type_to_converter_map[file_type]
    converter(origin_file, destination_file, metadata)

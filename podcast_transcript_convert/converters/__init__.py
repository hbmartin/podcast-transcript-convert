"""Converters from each supported transcript format to PodcastIndex JSON."""

from collections.abc import Callable
from pathlib import Path

from podcast_transcript_convert.converters.html_to_json import html_file_to_json_file
from podcast_transcript_convert.converters.json_to_json import json_file_to_json_file
from podcast_transcript_convert.converters.srt_to_json import srt_file_to_json_file
from podcast_transcript_convert.converters.vtt_to_json import vtt_file_to_json_file
from podcast_transcript_convert.converters.xml_to_json import xml_file_to_json_file
from podcast_transcript_convert.file_typing import FileType

type Converter = Callable[[str | Path, str | Path, dict | None], None]

FILE_CONVERTERS: dict[FileType, Converter] = {
    FileType.HTML: html_file_to_json_file,
    FileType.JSON: json_file_to_json_file,
    FileType.SRT: srt_file_to_json_file,
    FileType.VTT: vtt_file_to_json_file,
    FileType.XML: xml_file_to_json_file,
}

__all__ = [
    "FILE_CONVERTERS",
    "Converter",
    "html_file_to_json_file",
    "json_file_to_json_file",
    "srt_file_to_json_file",
    "vtt_file_to_json_file",
    "xml_file_to_json_file",
]

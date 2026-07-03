import json
from pathlib import Path

from podcast_transcript_convert.errors import NoStartTimeError
from podcast_transcript_convert.file_utils import read_text_robust, write_text_utf8


def _number_to_ts(seconds: float) -> str:
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _segment_to_line(segment: dict) -> str:
    try:
        start_time = _number_to_ts(segment["startTime"])
    except KeyError as e:
        raise NoStartTimeError from e
    try:
        speaker = f"{segment['speaker']}: "
    except KeyError:
        speaker = ""
    return f"({start_time}) {speaker}{segment['body']}"


def json_file_to_simple_file(
    origin_file: str | Path,
    destination_file: str | Path,
) -> None:
    try:
        data = json.loads(read_text_robust(origin_file))
    except json.JSONDecodeError as e:
        e.add_note(str(origin_file))
        raise

    try:
        segments = map(_segment_to_line, data["segments"])
    except NoStartTimeError as e:
        e.add_note(str(origin_file))
        raise

    write_text_utf8(destination_file, "\n".join(segments))

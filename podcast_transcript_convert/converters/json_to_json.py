import json
from pathlib import Path

from podcast_transcript_convert.errors import InvalidJsonError
from podcast_transcript_convert.file_utils import read_text_robust, write_text_utf8


def json_file_to_json_file(
    origin_file: str | Path,
    destination_file: str | Path,
    metadata: dict | None,
) -> None:
    try:
        data = json.loads(read_text_robust(origin_file))
    except json.JSONDecodeError as e:
        error = InvalidJsonError()
        error.add_note(str(origin_file))
        raise error from e

    if (
        not isinstance(data, dict)
        or not isinstance(data.get("version"), str)
        or not isinstance(data.get("segments"), list)
        or not all(isinstance(segment, dict) for segment in data["segments"])
    ):
        error = InvalidJsonError()
        error.add_note(str(origin_file))
        raise error

    if metadata:
        data["metadata"] = metadata

    write_text_utf8(destination_file, json.dumps(data, indent=4))

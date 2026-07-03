import json
from pathlib import Path

from loguru import logger  # type: ignore[import-not-found]

from podcast_transcript_convert.file_utils import read_text_robust, write_text_utf8


def json_file_to_json_file(
    origin_file: str | Path,
    destination_file: str | Path,
    metadata: dict | None,
) -> None:
    try:
        data = json.loads(read_text_robust(origin_file))
    except json.JSONDecodeError as e:
        e.add_note(str(origin_file))
        raise

    if "version" not in data or "segments" not in data:
        logger.error(f"Non-spec JSON file: {origin_file}")
        return

    if metadata:
        data["metadata"] = metadata

    write_text_utf8(destination_file, json.dumps(data, indent=4))

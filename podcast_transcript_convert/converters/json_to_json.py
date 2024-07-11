import json
from pathlib import Path

from loguru import logger  # type: ignore[import-not-found]


def json_file_to_json_file(
    origin_file: str,
    destination_file: str,
    metadata: dict | None,
) -> None:
    try:
        data = json.loads(Path(origin_file).read_text())
    except json.JSONDecodeError as e:
        e.add_note(origin_file)
        raise

    if "version" not in data or "segments" not in data:
        logger.error(f"Non-spec JSON file: {origin_file}")
        return

    if metadata:
        data["metadata"] = metadata

    Path(destination_file).write_text(
        data=json.dumps(
            data,
            indent=4,
        ),
    )

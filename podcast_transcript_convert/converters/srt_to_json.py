import re
from json import dumps
from pathlib import Path

from podcast_transcript_convert.errors import InvalidSrtError

_srt_split = re.compile(r"\n\n\d*\n")
_srt_block = re.compile(
    r"(\d+:\d+:\d+[,.]\d+)\s*-->\s*(\d+:\d+:\d+[,.]\d+)(\s*)(.*)",
    flags=re.DOTALL,
)


def _mts_to_secs_float(time_string: str) -> float:
    hours, minutes, seconds, milliseconds = map(
        int,
        time_string.replace(",", ":").replace(".", ":").split(":"),
    )
    return round((hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000), 3)


# See spec at:
# https://github.com/Podcastindex-org/podcast-namespace/blob/main/transcripts/transcripts.md
def _srt_block_to_dict(block: str) -> dict | None:
    if match := _srt_block.search(block):
        start = _mts_to_secs_float(match[1])
        end = _mts_to_secs_float(match[2])
        body = match[4].strip().replace("\n", " ")

        return {"startTime": start, "endTime": end, "body": body}

    raise InvalidSrtError(block)


def srt_to_podcast_dict(srt_string: str) -> dict:
    blocks = [
        item
        for item in _srt_split.split(srt_string)
        if not item.isspace() and item != ""
    ]

    return {
        "version": "1.0.0",
        "segments": list(map(_srt_block_to_dict, blocks)),
    }


def srt_file_to_json_file(
    srt_file: str | Path,
    json_file: str | Path,
    metadata: dict | None,
) -> None:
    srt_string = Path(srt_file).read_text()
    try:
        transcript_dict = srt_to_podcast_dict(srt_string)
        if metadata:
            transcript_dict["metadata"] = metadata
    except InvalidSrtError as e:
        e.add_note(srt_file)
        raise

    Path(json_file).write_text(
        data=dumps(transcript_dict, indent=4),
    )

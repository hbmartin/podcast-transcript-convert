import re
from json import dumps
from pathlib import Path

from podcast_transcript_convert.errors import InvalidSrtError
from podcast_transcript_convert.file_utils import read_text_robust, write_text_utf8
from podcast_transcript_convert.models import Segment, Transcript, split_speaker_prefix

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
def _srt_block_to_segment(block: str) -> Segment:
    if match := _srt_block.search(block):
        speaker, body = split_speaker_prefix(
            match[4].strip().replace("\n", " "),
        )
        return Segment(
            body=body,
            start_time=_mts_to_secs_float(match[1]),
            end_time=_mts_to_secs_float(match[2]),
            speaker=speaker,
        )

    raise InvalidSrtError(block)


def srt_to_podcast_dict(srt_string: str) -> dict:
    blocks = [
        item
        for item in _srt_split.split(srt_string)
        if not item.isspace() and item != ""
    ]

    return Transcript(
        segments=[_srt_block_to_segment(block) for block in blocks],
    ).to_dict()


def srt_file_to_json_file(
    srt_file: str | Path,
    json_file: str | Path,
    metadata: dict | None,
) -> None:
    srt_string = read_text_robust(srt_file)
    try:
        transcript_dict = srt_to_podcast_dict(srt_string)
        if metadata:
            transcript_dict["metadata"] = metadata
    except InvalidSrtError as e:
        e.add_note(str(srt_file))
        raise

    write_text_utf8(json_file, dumps(transcript_dict, indent=4))

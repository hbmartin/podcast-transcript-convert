from json import dumps
from pathlib import Path

import webvtt  # type: ignore[import-not-found]
from loguru import logger
from webvtt.errors import MalformedFileError

from podcast_transcript_convert.errors import InvalidVttError
from podcast_transcript_convert.file_utils import read_text_robust, write_text_utf8
from podcast_transcript_convert.models import Segment, Transcript, split_speaker_prefix

from .srt_to_json import _mts_to_secs_float


def _caption_to_segment(caption: webvtt.Caption) -> Segment:
    body = caption.text.strip().replace("\n", " ")
    if caption.voice:
        speaker = caption.voice
    else:
        speaker, body = split_speaker_prefix(body)
    return Segment(
        body=body,
        start_time=_mts_to_secs_float(caption.start),
        end_time=_mts_to_secs_float(caption.end),
        speaker=speaker,
    )


def vtt_to_podcast_dict(vtt_string: str) -> dict:
    try:
        vtt = webvtt.from_string(vtt_string)
    except MalformedFileError as e:
        raise InvalidVttError from e
    return Transcript(
        segments=[_caption_to_segment(caption) for caption in vtt.captions],
    ).to_dict()


# https://www.w3.org/TR/webvtt1/#file-structure
def vtt_file_to_json_file(
    vtt_file: str | Path,
    json_file: str | Path,
    metadata: dict | None,
) -> None:
    try:
        vtt_string = read_text_robust(vtt_file)
        transcript_dict = vtt_to_podcast_dict(vtt_string)
        if metadata:
            transcript_dict["metadata"] = metadata
    except InvalidVttError as e:
        e.add_note(str(vtt_file))
        raise
    except FileNotFoundError:
        logger.error(f"File not found: {vtt_file}")
        return
    write_text_utf8(json_file, dumps(transcript_dict, indent=4))

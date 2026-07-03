import re
from functools import reduce
from json import dumps
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from loguru import logger

from podcast_transcript_convert.errors import InvalidHtmlError, NoTranscriptFoundError
from podcast_transcript_convert.file_utils import read_text_robust, write_text_utf8
from podcast_transcript_convert.models import Segment, Transcript

_p_ts = re.compile(r"<p>\s*(\d+:)?\d+:\d+\s*</p>")
_ts = re.compile(r"^\s*(\d+:)?\d+:\d+\s*$")


def _ts_to_secs(time_string: str) -> float:
    parts = enumerate(map(int, reversed(time_string.split(":"))))
    secs = next(parts)[1]
    return reduce(lambda acc, part: acc + ((60 ** part[0]) * part[1]), parts, secs)


def _add_speaker(segments: list[Segment], speaker: str) -> None:
    if segments[-1].speaker is None:
        segments[-1].speaker = speaker
    else:
        segments.append(Segment(speaker=speaker))


def _add_start_time(segments: list[Segment], start_time: float) -> None:
    if segments[-1].start_time is None:
        segments[-1].start_time = start_time
    else:
        segments.append(Segment(start_time=start_time))


# https://github.com/Podcastindex-org/podcast-namespace/blob/main/transcripts/transcripts.md#html
def _html_to_segments(soup: BeautifulSoup) -> list[Segment]:
    segments: list[Segment] = [Segment()]
    body_tag = soup.body
    children = body_tag.children if body_tag is not None else soup.children
    for child in children:
        if not isinstance(child, Tag):
            continue
        if child.name == "cite":
            _add_speaker(segments, child.text.replace(":", "").strip())
        elif child.name == "time":
            _add_start_time(segments, _ts_to_secs(child.text.strip()))
        elif child.name == "p" and (stripped := child.text.strip()):
            if _ts.match(stripped):
                _add_start_time(segments, _ts_to_secs(stripped))
            else:
                segments[-1].body = stripped
    if not segments[0].to_dict():
        raise NoTranscriptFoundError
    return segments


def html_to_podcast_dict(html_string: str) -> dict:
    if "<cite>" in html_string or "<time>" in html_string or _p_ts.match(html_string):
        soup = BeautifulSoup(html_string, "html.parser")
    else:
        raise InvalidHtmlError

    return Transcript(segments=_html_to_segments(soup)).to_dict()


def html_file_to_json_file(
    html_file: str | Path,
    json_file: str | Path,
    metadata: dict | None,
) -> None:
    try:
        html_string = read_text_robust(html_file)
        transcript_dict = html_to_podcast_dict(html_string)
        if metadata:
            transcript_dict["metadata"] = metadata
    except (InvalidHtmlError, NoTranscriptFoundError, ValueError) as e:
        e.add_note(str(html_file))
        raise
    except FileNotFoundError:
        logger.error(f"File not found: {html_file}")
        return

    write_text_utf8(json_file, dumps(transcript_dict, indent=4))

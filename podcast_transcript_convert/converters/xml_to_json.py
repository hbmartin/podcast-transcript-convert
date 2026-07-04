from json import dumps
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from podcast_transcript_convert.errors import InvalidXmlError, NoTranscriptFoundError
from podcast_transcript_convert.file_utils import read_text_robust, write_text_utf8
from podcast_transcript_convert.models import Segment, Transcript

from .srt_to_json import _mts_to_secs_float


def _xml_to_segments(soup: BeautifulSoup) -> list[Segment]:
    segments: list[Segment] = [Segment()]
    transcripts = soup.find("transcripts")
    if not isinstance(transcripts, Tag):
        raise NoTranscriptFoundError
    for child in transcripts.children:
        if isinstance(child, Tag) and child.name == "speech":
            if segments[-1].body is not None:
                segments.append(Segment())
            for item in child.children:
                if isinstance(item, Tag) and item.name == "item":
                    if segments[-1].body is None:
                        segments[-1].body = item.text
                    else:
                        segments[-1].body += f" {item.text}"

                    if segments[-1].start_time is None:
                        segments[-1].start_time = _mts_to_secs_float(str(item["start"]))

                    segments[-1].end_time = _mts_to_secs_float(str(item["end"]))
    populated_segments = [segment for segment in segments if segment.to_dict()]
    if not populated_segments:
        raise NoTranscriptFoundError
    return populated_segments


def xml_to_podcast_dict(xml_string: str) -> dict:
    if "http://podlove.org/simple-transcripts" in xml_string:
        soup = BeautifulSoup(xml_string, "lxml-xml")
    else:
        raise InvalidXmlError

    return Transcript(segments=_xml_to_segments(soup)).to_dict()


def xml_file_to_json_file(
    xml_file: str | Path,
    json_file: str | Path,
    metadata: dict | None,
) -> None:
    xml_string = read_text_robust(xml_file)
    try:
        transcript_dict = xml_to_podcast_dict(xml_string)
        if metadata:
            transcript_dict["metadata"] = metadata
    except InvalidXmlError as e:
        e.add_note(str(xml_file))
        raise

    write_text_utf8(json_file, dumps(transcript_dict, indent=4))

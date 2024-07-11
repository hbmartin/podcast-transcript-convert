from json import dumps
from pathlib import Path
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, PageElement

from podcast_transcript_convert.errors import InvalidXmlError, NoTranscriptFoundError

from .srt_to_json import _mts_to_secs_float

if TYPE_CHECKING:
    from collections.abc import Iterable


def _xml_to_list(soup: BeautifulSoup) -> list[dict]:
    blocks: list[dict] = [{}]
    children: Iterable[PageElement] = soup.transcripts.children  # type: ignore[attr-defined]
    for child in children:
        if child.name == "speech":  # type: ignore[attr-defined]
            if "body" in blocks[-1]:
                blocks.append({})
            for item in child.children:  # type: ignore[attr-defined]
                if item.name == "item":
                    if "body" not in blocks[-1]:
                        blocks[-1]["body"] = item.text
                    else:
                        blocks[-1]["body"] += f" {item.text}"

                    if "startTime" not in blocks[-1]:
                        blocks[-1]["startTime"] = _mts_to_secs_float(item["start"])

                    blocks[-1]["endTime"] = _mts_to_secs_float(item["end"])
    if blocks[0] == {}:
        raise NoTranscriptFoundError
    return blocks


def xml_to_podcast_dict(xml_string: str) -> dict:
    if "http://podlove.org/simple-transcripts" in xml_string:
        soup = BeautifulSoup(xml_string, "lxml-xml")
    else:
        raise InvalidXmlError

    return {
        "version": "1.0.0",
        "segments": _xml_to_list(soup),
    }


def xml_file_to_json_file(xml_file: str, json_file: str, metadata: dict | None) -> None:
    xml_string = Path(xml_file).read_text()
    try:
        transcript_dict = xml_to_podcast_dict(xml_string)
        if metadata:
            transcript_dict["metadata"] = metadata
    except InvalidXmlError as e:
        e.add_note(xml_file)
        raise

    Path(json_file).write_text(
        data=dumps(transcript_dict, indent=4),
    )

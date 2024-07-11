import re
from functools import reduce
from json import dumps
from pathlib import Path
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, PageElement
from loguru import logger

from podcast_transcript_convert.errors import InvalidHtmlError, NoTranscriptFoundError

if TYPE_CHECKING:
    from collections.abc import Iterable


_p_ts = re.compile(r"<p>\s*(\d+:)?\d+:\d+\s*</p>")
_ts = re.compile(r"^\s*(\d+:)?\d+:\d+\s*$")


def _ts_to_secs(time_string: str) -> float:
    parts = enumerate(map(int, reversed(time_string.split(":"))))
    secs = next(parts)[1]
    return reduce(lambda acc, part: acc + ((60 ** part[0]) * part[1]), parts, secs)


# https://github.com/Podcastindex-org/podcast-namespace/blob/main/transcripts/transcripts.md#html
def _html_to_list(soup: BeautifulSoup) -> list[dict]:  # noqa: PLR0912
    blocks: list[dict] = [{}]
    children: Iterable[PageElement] = soup.body.children if soup.body else soup.children  # type: ignore[attr-defined]
    for child in children:
        if child.name == "cite":  # type: ignore[attr-defined]
            if "speaker" not in blocks[-1]:
                blocks[-1]["speaker"] = child.text.replace(":", "").strip()
            else:
                blocks.append(
                    {
                        "speaker": child.text.replace(":", "").strip(),
                    },
                )
        elif child.name == "time":  # type: ignore[attr-defined]
            if "startTime" not in blocks[-1]:
                blocks[-1]["startTime"] = _ts_to_secs(child.text.strip())
            else:
                blocks.append(
                    {
                        "startTime": _ts_to_secs(child.text.strip()),
                    },
                )
        elif child.name == "p" and (stripped := child.text.strip()):  # type: ignore[attr-defined]
            if _ts.match(stripped):
                if "startTime" not in blocks[-1]:
                    blocks[-1]["startTime"] = _ts_to_secs(stripped)
                else:
                    blocks.append(
                        {
                            "startTime": _ts_to_secs(stripped),
                        },
                    )
            else:
                blocks[-1]["body"] = stripped
    if blocks[0] == {}:
        raise NoTranscriptFoundError
    return blocks


def html_to_podcast_dict(html_string: str) -> dict:
    if "<cite>" in html_string or "<time>" in html_string or _p_ts.match(html_string):
        soup = BeautifulSoup(html_string, "html.parser")
    else:
        raise InvalidHtmlError

    return {
        "version": "1.0.0",
        "segments": _html_to_list(soup),
    }


def html_file_to_json_file(
    html_file: str | Path,
    json_file: str | Path,
    metadata: dict | None,
) -> None:
    try:
        html_string = Path(html_file).read_text()
        transcript_dict = html_to_podcast_dict(html_string)
        if metadata:
            transcript_dict["metadata"] = metadata
    except InvalidHtmlError as e:
        e.add_note(html_file)
        raise
    except NoTranscriptFoundError as e:
        e.add_note(html_file)
        raise
    except ValueError as e:
        e.add_note(html_file)
        raise
    except FileNotFoundError:
        logger.error(f"File not found: {html_file}")
        return

    Path(json_file).write_text(
        data=dumps(transcript_dict, indent=4),
    )

import json
from pathlib import Path

import pytest

from podcast_transcript_convert.converters.xml_to_json import (
    xml_file_to_json_file,
    xml_to_podcast_dict,
)
from podcast_transcript_convert.errors import InvalidXmlError, NoTranscriptFoundError

PODLOVE_XML = (
    '<?xml version="1.0"?>'
    '<podcast:transcripts xmlns:podcast="http://podlove.org/simple-transcripts">'
    '<speech><item start="00:00:00.000" end="00:00:01.000">Hello</item></speech>'
    "</podcast:transcripts>"
)


def test_xml_to_podcast_dict():
    html_string = Path(
        "tests/fixtures/Hunting CrossSite Scripting on the Web.xsl",
    ).read_text()
    transcript_dict = xml_to_podcast_dict(html_string)
    assert transcript_dict["segments"][0]["body"] == "Welcome to"
    assert transcript_dict["segments"][0]["startTime"] == 0.82
    assert transcript_dict["segments"][0]["endTime"] == 1.66
    assert (
        transcript_dict["segments"][-1]["body"]
        == """
thanks everyone out there who listened to "The Open Source Way". If you enjoyed this episode, please share it and don't miss the next one. We usually publish every last Wednesday of the month, and you'll find us on openSAP and in all those places where you find your other podcasts . Either the mainstream apps that you know, or some of the, themselves, open-source podcast apps. Thanks again and bye bye.
    """.strip()
    )
    assert transcript_dict["segments"][-1]["startTime"] == 1739.4
    assert transcript_dict["segments"][-1]["endTime"] == 1766.55


def test_xml_to_podcast_dict_drops_empty_speech_segments():
    xml_string = """<?xml version="1.0"?>
    <podcast:transcripts xmlns:podcast="http://podlove.org/simple-transcripts">
        <speech>
            <item start="00:00:00.000" end="00:00:01.000">Hello</item>
        </speech>
        <speech></speech>
    </podcast:transcripts>
    """

    transcript_dict = xml_to_podcast_dict(xml_string)

    assert transcript_dict["segments"] == [
        {"startTime": 0.0, "endTime": 1.0, "body": "Hello"},
    ]


def test_xml_to_podcast_dict_not_podlove_raises():
    with pytest.raises(InvalidXmlError):
        xml_to_podcast_dict('<?xml version="1.0"?><root><speech/></root>')


def test_xml_to_podcast_dict_without_transcripts_tag_raises():
    xml_string = (
        '<?xml version="1.0"?>'
        '<root xmlns:podcast="http://podlove.org/simple-transcripts">'
        "<other>hi</other></root>"
    )
    with pytest.raises(NoTranscriptFoundError):
        xml_to_podcast_dict(xml_string)


def test_xml_to_podcast_dict_only_empty_speech_raises():
    xml_string = (
        '<?xml version="1.0"?>'
        '<podcast:transcripts xmlns:podcast="http://podlove.org/simple-transcripts">'
        "<speech></speech>"
        "</podcast:transcripts>"
    )
    with pytest.raises(NoTranscriptFoundError):
        xml_to_podcast_dict(xml_string)


def test_xml_file_to_json_file_writes_json_with_metadata(tmp_path: Path):
    source = tmp_path / "ep.xml"
    source.write_text(PODLOVE_XML)
    destination = tmp_path / "ep.json"

    xml_file_to_json_file(source, destination, {"title": "Episode 1"})

    data = json.loads(destination.read_text())
    assert data["metadata"] == {"title": "Episode 1"}
    assert data["segments"][0]["body"] == "Hello"


def test_xml_file_to_json_file_invalid_raises_and_writes_nothing(tmp_path: Path):
    source = tmp_path / "bad.xml"
    source.write_text('<?xml version="1.0"?><root></root>')
    destination = tmp_path / "out.json"

    with pytest.raises(InvalidXmlError) as excinfo:
        xml_file_to_json_file(source, destination, None)

    assert str(source) in excinfo.value.__notes__
    assert not destination.exists()

import json
from pathlib import Path

import pytest

from podcast_transcript_convert.converters.html_to_json import (
    _ts_to_secs,
    html_file_to_json_file,
    html_to_podcast_dict,
)
from podcast_transcript_convert.errors import InvalidHtmlError, NoTranscriptFoundError


def test__ts_to_secs():
    assert _ts_to_secs("00:00:00") == 0
    assert _ts_to_secs("01:31") == 91
    assert _ts_to_secs("02:01:31") == 7291
    with pytest.raises(ValueError):
        _ts_to_secs("abc")
    with pytest.raises(ValueError):
        _ts_to_secs("")


def test_html_to_podcast_dict_no_time():
    html_string = Path("tests/fixtures/300 multiple choices.html").read_text()
    transcript_dict = html_to_podcast_dict(html_string)
    assert transcript_dict["version"] == "1.0.0"
    assert len(transcript_dict["segments"]) == 307
    assert (
        transcript_dict["segments"][0]["body"]
        == "Welcome to Go Time. This is a very special episode. This is episode number 300. So today we're doing something a little different from our usual content. We're having a full panel episode with our co-hosts, with all of our hosts... And we're talking about the past of Go Time, the current present, and our plans for the future. So joining me live is Jon Calhoun. How are you doing, Jon?"
    )
    assert transcript_dict["segments"][0]["speaker"] == "Kris Brandow"
    assert transcript_dict["segments"][-1]["speaker"] == "Kris Brandow"


def test_html_to_podcast_dict_no_body():
    html_string = Path(
        "tests/fixtures/Talking AI at OpenShift Commons Gathering in Raleigh.html",
    ).read_text()
    transcript_dict = html_to_podcast_dict(html_string)
    assert transcript_dict["version"] == "1.0.0"
    assert len(transcript_dict["segments"]) == 131
    assert (
        transcript_dict["segments"][0]["body"]
        == "Now for something completely different. Frank is in Raleigh speaking at"
    )
    assert transcript_dict["segments"][0]["speaker"] == "Speaker"
    assert transcript_dict["segments"][0]["startTime"] == 0
    assert transcript_dict["segments"][-1]["body"] == "Thanks. And you"
    assert transcript_dict["segments"][-1]["speaker"] == "Speaker"
    assert transcript_dict["segments"][-1]["startTime"] == 511


def test_html_to_podcast_dict_no_cite_or_time():
    html_string = "<html><body><p>Just a paragraph</p></body></html>"
    with pytest.raises(InvalidHtmlError):
        html_to_podcast_dict(html_string)


def test_html_to_podcast_dict_with_ts_in_p_tag():
    html_string = Path(
        "tests/fixtures/78 Exploring MCMC Sampler Algorithms, with Matt D. Hoffman.html",
    ).read_text()
    transcript_dict = html_to_podcast_dict(html_string)
    assert len(transcript_dict["segments"]) == 104
    assert (
        transcript_dict["segments"][0]["body"]
        == "Okay, I mean now, can you hear me well yes. Okay, can I hear you don't need to"
    )
    assert transcript_dict["segments"][0]["startTime"] == 119
    assert transcript_dict["segments"][-1]["body"] == "Thank you. You too. Bye."
    assert transcript_dict["segments"][-1]["startTime"] == 5254


def test_html_to_podcast_dict_with_ts_looking_in_body():
    html_string = Path(
        "tests/fixtures/Tales from Manufacturing Shipping Rack 1.html",
    ).read_text()
    transcript_dict = html_to_podcast_dict(html_string)
    assert transcript_dict["segments"][0]["speaker"] == "Speaker 1"
    assert transcript_dict["segments"][0]["startTime"] == 0
    assert transcript_dict["segments"][-1]["speaker"] == "Speaker 2"
    assert transcript_dict["segments"][-1]["startTime"] == 5051


def test_html_to_podcast_dict_empty():
    with pytest.raises(InvalidHtmlError):
        html_to_podcast_dict("")


def test_html_to_podcast_dict_no_usable_transcript_content():
    # "<time>" as a substring passes the format gate, but the parsed document
    # holds no cite/time/p content, so no segment is populated.
    html_string = "<!-- <time> --><div>hello</div>"
    with pytest.raises(NoTranscriptFoundError):
        html_to_podcast_dict(html_string)


def test_html_file_to_json_file_writes_json_with_metadata(tmp_path: Path):
    source = tmp_path / "ep.html"
    source.write_text(
        "<html><body><cite>Ann:</cite><p>Hello there</p></body></html>",
    )
    destination = tmp_path / "ep.json"

    html_file_to_json_file(source, destination, {"title": "Episode 1"})

    data = json.loads(destination.read_text())
    assert data["metadata"] == {"title": "Episode 1"}
    assert data["segments"][0]["speaker"] == "Ann"
    assert data["segments"][0]["body"] == "Hello there"


def test_html_file_to_json_file_invalid_raises_and_writes_nothing(tmp_path: Path):
    source = tmp_path / "bad.html"
    source.write_text("<html><body><p>no cite or time here</p></body></html>")
    destination = tmp_path / "out.json"

    with pytest.raises(InvalidHtmlError) as excinfo:
        html_file_to_json_file(source, destination, None)

    assert str(source) in excinfo.value.__notes__
    assert not destination.exists()


def test_html_file_to_json_file_missing_file_raises(tmp_path: Path):
    destination = tmp_path / "out.json"

    with pytest.raises(FileNotFoundError):
        html_file_to_json_file(tmp_path / "missing.html", destination, None)

    assert not destination.exists()

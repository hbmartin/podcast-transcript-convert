import json
from pathlib import Path

import pytest

from podcast_transcript_convert.converters.vtt_to_json import (
    vtt_file_to_json_file,
    vtt_to_podcast_dict,
)
from podcast_transcript_convert.errors import InvalidVttError

VALID_VTT = "WEBVTT\n\n00:00.000 --> 00:01.000\nHello from VTT.\n"


def test_vtt_to_podcast_dict_with_speaker_tags():
    srt_string = Path(
        "tests/fixtures/Labs Setting Engineering Goals and Reporting to Stakeholders.txt",
    ).read_text()
    transcript_dict = vtt_to_podcast_dict(srt_string)
    assert transcript_dict["version"] == "1.0.0"
    assert len(transcript_dict["segments"]) == 494
    assert (
        transcript_dict["segments"][0]["body"]
        == "We need to remember that less is more."
    )
    assert transcript_dict["segments"][0]["startTime"] == 0.0
    assert transcript_dict["segments"][0]["endTime"] == 2.310
    assert transcript_dict["segments"][0]["speaker"] == "Yishai Beeri"
    assert transcript_dict["segments"][-1]["startTime"] == 2271.601
    assert transcript_dict["segments"][-1]["endTime"] == 2272.891
    assert transcript_dict["segments"][-1]["body"] == "Talk again soon."
    assert transcript_dict["segments"][-1]["speaker"] == "Dan Lines"


def test_vtt_to_podcast_dict_with_some_speaker_and_note():
    srt_string = Path("tests/fixtures/Managed services vs. DIY.vtt").read_text()
    transcript_dict = vtt_to_podcast_dict(srt_string)
    assert transcript_dict["version"] == "1.0.0"
    assert len(transcript_dict["segments"]) == 576
    assert transcript_dict["segments"][0]["startTime"] == 0.038
    assert transcript_dict["segments"][0]["endTime"] == 3.938
    assert (
        transcript_dict["segments"][0]["body"]
        == "Hello, and welcome to Postgres FM, a new weekly show"
    )
    assert transcript_dict["segments"][0]["speaker"] == "Michael"
    assert transcript_dict["segments"][-1]["startTime"] == 1971.997
    assert transcript_dict["segments"][-1]["endTime"] == 1972.267
    assert transcript_dict["segments"][-1]["body"] == "Bye."
    assert transcript_dict["segments"][-1]["speaker"] == "Nikolay"


def test_vtt_to_podcast_dict_with_numbered_blocks():
    srt_string = Path(
        "tests/fixtures/Zenlytic Is Building You A Better Coworker With AI Agents.txt",
    ).read_text()
    transcript_dict = vtt_to_podcast_dict(srt_string)
    assert transcript_dict["version"] == "1.0.0"
    assert len(transcript_dict["segments"]) == 727
    assert transcript_dict["segments"][0]["startTime"] == 0.0
    assert transcript_dict["segments"][0]["endTime"] == 15.359
    assert (
        transcript_dict["segments"][0]["body"]
        == "Hello, and welcome to the Data Engineering Podcast, the show about modern data management."
    )
    assert "speaker" not in transcript_dict["segments"][0]
    assert transcript_dict["segments"][-1]["startTime"] == 3249.44
    assert transcript_dict["segments"][-1]["endTime"] == 3251.44
    assert (
        transcript_dict["segments"][-1]["body"]
        == "Podcasts and tell your friends and coworkers."
    )


def test_vtt_to_podcast_dict_with_invalid():
    with pytest.raises(InvalidVttError):
        vtt_to_podcast_dict("")


def test_vtt_file_to_json_file_with_metadata(tmp_path: Path):
    source = tmp_path / "ep.vtt"
    source.write_text(VALID_VTT)
    destination = tmp_path / "ep.json"

    vtt_file_to_json_file(source, destination, {"title": "Episode 1"})

    data = json.loads(destination.read_text())
    assert data["metadata"] == {"title": "Episode 1"}
    assert data["segments"][0]["body"] == "Hello from VTT."


def test_vtt_file_to_json_file_invalid_raises_and_writes_nothing(tmp_path: Path):
    source = tmp_path / "bad.vtt"
    source.write_text("this is not a valid vtt file")
    destination = tmp_path / "out.json"

    with pytest.raises(InvalidVttError) as excinfo:
        vtt_file_to_json_file(source, destination, None)

    assert str(source) in excinfo.value.__notes__
    assert not destination.exists()


def test_vtt_file_to_json_file_missing_file_raises(tmp_path: Path):
    destination = tmp_path / "out.json"

    with pytest.raises(FileNotFoundError):
        vtt_file_to_json_file(tmp_path / "missing.vtt", destination, None)

    assert not destination.exists()

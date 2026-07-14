import json
from pathlib import Path

import pytest

from podcast_transcript_convert.converters.any_to_simple import (
    transcript_file_to_simple_file,
)
from podcast_transcript_convert.converters.json_to_simple import (
    _number_to_ts,
    json_file_to_simple_file,
)
from podcast_transcript_convert.errors import NoStartTimeError, UnknownFileTypeError

VALID_SRT = "1\n00:00:00,000 --> 00:00:01,000\nMichael: Hello world.\n\n"


def test_number_to_ts():
    assert _number_to_ts(0) == "00:00:00"
    assert _number_to_ts(61.5) == "00:01:01"
    assert _number_to_ts(3661) == "01:01:01"


def test_json_file_to_simple_file(tmp_path: Path):
    origin = tmp_path / "ep.json"
    origin.write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "segments": [
                    {"startTime": 0.0, "body": "Hello.", "speaker": "Ann"},
                    {"startTime": 61.0, "body": "Goodbye."},
                ],
            },
        ),
    )
    destination = tmp_path / "ep.txt"

    json_file_to_simple_file(origin, destination)

    assert destination.read_text() == ("(00:00:00) Ann: Hello.\n(00:01:01) Goodbye.")


def test_json_file_to_simple_file_without_start_time(tmp_path: Path):
    origin = tmp_path / "ep.json"
    origin.write_text(json.dumps({"segments": [{"body": "Hello."}]}))

    with pytest.raises(NoStartTimeError) as excinfo:
        json_file_to_simple_file(origin, tmp_path / "ep.txt")

    assert str(origin) in excinfo.value.__notes__


def test_json_file_to_simple_file_invalid_json_raises(tmp_path: Path):
    origin = tmp_path / "ep.json"
    origin.write_text("{not valid json")

    with pytest.raises(json.JSONDecodeError) as excinfo:
        json_file_to_simple_file(origin, tmp_path / "ep.txt")

    assert str(origin) in excinfo.value.__notes__


def test_transcript_file_to_simple_file(tmp_path: Path):
    origin = tmp_path / "ep.srt"
    origin.write_text(VALID_SRT)
    destination = tmp_path / "ep.json"

    transcript_file_to_simple_file(origin, destination)

    data = json.loads(destination.read_text())
    assert data["segments"][0]["speaker"] == "Michael"


def test_transcript_file_to_simple_file_unknown(tmp_path: Path):
    origin = tmp_path / "mystery.bin"
    origin.write_text("not a transcript")

    with pytest.raises(UnknownFileTypeError):
        transcript_file_to_simple_file(origin, tmp_path / "out.json")

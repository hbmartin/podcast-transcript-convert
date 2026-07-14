import json
from pathlib import Path

import pytest

from podcast_transcript_convert.converters.json_to_json import json_file_to_json_file

SPEC_JSON = {
    "version": "1.0.0",
    "segments": [{"startTime": 0.0, "body": "Hello world."}],
}


def test_json_file_to_json_file_copies_spec_file(tmp_path: Path):
    origin = tmp_path / "in.json"
    origin.write_text(json.dumps(SPEC_JSON))
    destination = tmp_path / "out.json"

    json_file_to_json_file(origin, destination, None)

    data = json.loads(destination.read_text())
    assert data["version"] == "1.0.0"
    assert data["segments"][0]["body"] == "Hello world."
    assert "metadata" not in data


def test_json_file_to_json_file_adds_metadata(tmp_path: Path):
    origin = tmp_path / "in.json"
    origin.write_text(json.dumps(SPEC_JSON))
    destination = tmp_path / "out.json"

    json_file_to_json_file(origin, destination, {"title": "Episode 1"})

    data = json.loads(destination.read_text())
    assert data["metadata"] == {"title": "Episode 1"}


def test_json_file_to_json_file_non_spec_file_is_skipped(tmp_path: Path):
    origin = tmp_path / "in.json"
    origin.write_text(json.dumps({"foo": "bar"}))
    destination = tmp_path / "out.json"

    json_file_to_json_file(origin, destination, None)

    assert not destination.exists()


def test_json_file_to_json_file_missing_segments_is_skipped(tmp_path: Path):
    origin = tmp_path / "in.json"
    origin.write_text(json.dumps({"version": "1.0.0"}))
    destination = tmp_path / "out.json"

    json_file_to_json_file(origin, destination, None)

    assert not destination.exists()


def test_json_file_to_json_file_invalid_json_raises(tmp_path: Path):
    origin = tmp_path / "in.json"
    origin.write_text("{not valid json")
    destination = tmp_path / "out.json"

    with pytest.raises(json.JSONDecodeError) as excinfo:
        json_file_to_json_file(origin, destination, None)

    assert str(origin) in excinfo.value.__notes__
    assert not destination.exists()

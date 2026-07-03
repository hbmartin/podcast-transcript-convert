import json
from pathlib import Path

import pytest

from podcast_transcript_convert.__main__ import build_parser, main

VALID_SRT = "1\n00:00:00,000 --> 00:00:01,000\nMichael: Hello world.\n\n"


def test_help_exits_zero(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as excinfo:
        build_parser().parse_args(["--help"])
    assert excinfo.value.code == 0
    assert "usage: transcript2json" in capsys.readouterr().out


def test_version_exits_zero(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as excinfo:
        build_parser().parse_args(["--version"])
    assert excinfo.value.code == 0
    assert "transcript2json" in capsys.readouterr().out


def test_missing_arguments_exits_nonzero():
    with pytest.raises(SystemExit) as excinfo:
        build_parser().parse_args([])
    assert excinfo.value.code == 2


def test_main_bulk_conversion(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "in"
    source.mkdir()
    (source / "ep.srt").write_text(VALID_SRT)
    destination = tmp_path / "out"

    assert main([str(source), str(destination)]) == 0
    assert (destination / "ep.json").exists()


def test_main_single_file_to_directory(tmp_path: Path):
    source = tmp_path / "ep.srt"
    source.write_text(VALID_SRT)
    destination = tmp_path / "out"

    assert main([str(source), str(destination)]) == 0

    data = json.loads((destination / "ep.json").read_text())
    assert data["segments"][0]["body"] == "Hello world."


def test_main_single_file_to_file(tmp_path: Path):
    source = tmp_path / "ep.srt"
    source.write_text(VALID_SRT)
    destination = tmp_path / "converted.json"

    assert main([str(source), str(destination)]) == 0
    assert destination.exists()


def test_main_single_file_failure_exits_nonzero(tmp_path: Path):
    source = tmp_path / "bad.srt"
    source.write_text("this is not valid srt")

    assert main([str(source), str(tmp_path / "out.json")]) == 1


def test_main_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "in"
    source.mkdir()
    (source / "ep.srt").write_text(VALID_SRT)
    destination = tmp_path / "out"

    assert main(["--dry-run", str(source), str(destination)]) == 0
    assert not (destination / "ep.json").exists()


def test_main_ignore_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "in"
    source.mkdir()
    (source / "ep.srt").write_text(VALID_SRT)
    (source / "skipme.srt").write_text(VALID_SRT)
    ignore_file = tmp_path / "myignore"
    ignore_file.write_text("skipme.srt\n")
    destination = tmp_path / "out"

    assert main(["--ignore-file", str(ignore_file), str(source), str(destination)]) == 0
    assert (destination / "ep.json").exists()
    assert not (destination / "skipme.json").exists()


def test_main_default_transcriptignore(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "in"
    source.mkdir()
    (source / "ep.srt").write_text(VALID_SRT)
    (source / "skipme.srt").write_text(VALID_SRT)
    (tmp_path / ".transcriptignore").write_text("skipme.srt\n")
    destination = tmp_path / "out"

    assert main([str(source), str(destination)]) == 0
    assert (destination / "ep.json").exists()
    assert not (destination / "skipme.json").exists()

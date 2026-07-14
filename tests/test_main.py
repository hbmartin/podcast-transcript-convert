import json
import runpy
import sys
from importlib.metadata import PackageNotFoundError
from pathlib import Path

import pytest
from loguru import logger

import podcast_transcript_convert.__main__ as main_module
from podcast_transcript_convert.__main__ import _package_version, build_parser, main

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


def test_main_single_file_dry_run_writes_nothing(tmp_path: Path):
    source = tmp_path / "ep.srt"
    source.write_text(VALID_SRT)
    destination = tmp_path / "out"

    assert main(["--dry-run", str(source), str(destination)]) == 0
    assert not destination.exists()


def test_main_single_file_skips_existing_unless_overwrite(tmp_path: Path):
    source = tmp_path / "ep.srt"
    source.write_text(VALID_SRT)
    destination = tmp_path / "converted.json"
    destination.write_text("original")

    assert main([str(source), str(destination)]) == 1
    assert destination.read_text() == "original"

    assert main(["--overwrite", str(source), str(destination)]) == 0
    data = json.loads(destination.read_text())
    assert data["segments"][0]["body"] == "Hello world."


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
    assert not destination.exists()


def test_main_bulk_partial_failure_exits_nonzero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "in"
    source.mkdir()
    (source / "good.srt").write_text(VALID_SRT)
    (source / "bad.srt").write_text("this is not valid srt")
    destination = tmp_path / "out"

    assert main([str(source), str(destination)]) == 1
    assert (destination / "good.json").exists()


def test_main_bulk_unknown_only_exits_nonzero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "in"
    source.mkdir()
    (source / "mystery.bin").write_text("not a transcript")
    destination = tmp_path / "out"

    assert main([str(source), str(destination)]) == 1


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


def test_main_quiet_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "ep.srt"
    source.write_text(VALID_SRT)
    destination = tmp_path / "out"

    try:
        assert main(["--quiet", str(source), str(destination)]) == 0
    finally:
        # main(--quiet) reconfigures the global loguru logger; restore a
        # default handler so it does not leak into other tests.
        logger.remove()
        logger.add(sys.stderr)

    assert (destination / "ep.json").exists()


def test_package_version_returns_installed_version():
    assert _package_version() != "unknown"


def test_package_version_unknown_when_not_installed(monkeypatch: pytest.MonkeyPatch):
    def raise_not_found(_name: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr(main_module, "version", raise_not_found)
    assert _package_version() == "unknown"


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_module_entrypoint_runs_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    source = tmp_path / "ep.srt"
    source.write_text(VALID_SRT)
    destination = tmp_path / "converted.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["transcript2json", str(source), str(destination)],
    )

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("podcast_transcript_convert.__main__", run_name="__main__")

    assert excinfo.value.code == 0
    assert destination.exists()

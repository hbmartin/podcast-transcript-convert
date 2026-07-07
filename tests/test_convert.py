import json
from pathlib import Path

import pytest

import podcast_transcript_convert.convert as convert_module
from podcast_transcript_convert.convert import (
    _assign_destinations,
    _destination_path,
    bulk_convert,
    convert_file,
)
from podcast_transcript_convert.errors import UnknownFileTypeError

VALID_SRT = "1\n00:00:00,000 --> 00:00:01,000\nMichael: Hello world.\n\n"
VALID_VTT = "WEBVTT\n\n00:00.000 --> 00:01.000\nHello from VTT.\n"


def test_destination_path_mirrors_source_root():
    dest = _destination_path("/src/show/ep.srt", "/out", source_root="/src")
    assert dest == Path("/out/show/ep.json")


def test_destination_path_nested_dirs_do_not_collide():
    dest_a = _destination_path("/src/show a/deep/ep.srt", "/out", source_root="/src")
    dest_b = _destination_path("/src/show b/deep/ep.srt", "/out", source_root="/src")
    assert dest_a != dest_b


def test_destination_path_without_source_root_uses_parent_name():
    dest = _destination_path("/anywhere/show/ep.srt", "/out")
    assert dest == Path("/out/show/ep.json")


def test_destination_path_bare_filename():
    assert _destination_path("ep.srt", "/out") == Path("/out/ep.json")
    assert _destination_path("/ep.srt", "/out") == Path("/out/ep.json")


def test_assign_destinations_dedupes_collisions():
    destinations = _assign_destinations(
        ["/db/show/ep.srt", "/db/show/ep.vtt"],
        "/out",
        source_root=None,
    )
    assert destinations["/db/show/ep.srt"] == Path("/out/show/ep.json")
    assert destinations["/db/show/ep.vtt"] == Path("/out/show/ep (1).json")


def test_convert_file_srt(tmp_path: Path):
    source = tmp_path / "ep.srt"
    source.write_text(VALID_SRT)
    destination = tmp_path / "ep.json"

    convert_file(source, destination)

    data = json.loads(destination.read_text())
    assert data["version"] == "1.0.0"
    assert data["segments"][0]["speaker"] == "Michael"
    assert data["segments"][0]["body"] == "Hello world."


def test_convert_file_unknown_type(tmp_path: Path):
    source = tmp_path / "mystery.bin"
    source.write_text("not a transcript")

    with pytest.raises(UnknownFileTypeError):
        convert_file(source, tmp_path / "out.json")


def test_bulk_convert(tmp_path: Path):
    source = tmp_path / "in"
    (source / "show").mkdir(parents=True)
    (source / "show" / "ep1.srt").write_text(VALID_SRT)
    (source / "show" / "ep2.vtt").write_text(VALID_VTT)
    (source / "mystery.bin").write_text("not a transcript")
    destination = tmp_path / "out"

    summary = bulk_convert(str(source), str(destination))

    assert len(summary.converted) == 2
    assert summary.failed == []
    assert summary.unknown == [str(source / "mystery.bin")]
    assert (destination / "show" / "ep1.json").exists()
    assert (destination / "show" / "ep2.json").exists()


def test_bulk_convert_continues_after_failure(tmp_path: Path):
    source = tmp_path / "in"
    source.mkdir()
    (source / "bad.srt").write_text("this is not valid srt")
    (source / "good.srt").write_text(VALID_SRT)
    destination = tmp_path / "out"

    summary = bulk_convert(str(source), str(destination))

    assert [src for src, _ in summary.converted] == [str(source / "good.srt")]
    assert [src for src, _ in summary.failed] == [str(source / "bad.srt")]
    assert (destination / "good.json").exists()


def test_bulk_convert_records_missing_vtt_as_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    missing = tmp_path / "missing.vtt"
    destination = tmp_path / "out"

    def missing_vtt_from_db(
        db_path: str,
        ignore: list[str],
    ) -> tuple[list[str], dict[str, dict[str, str]]]:
        assert db_path == str(tmp_path / "overcast.db")
        assert ignore == []
        return [str(missing)], {}

    monkeypatch.setattr(
        convert_module,
        "list_files_from_db",
        missing_vtt_from_db,
    )

    summary = convert_module.bulk_convert(
        str(tmp_path / "overcast.db"), str(destination)
    )

    assert summary.converted == []
    assert [src for src, _ in summary.failed] == [str(missing)]
    assert list(destination.rglob("*.json")) == []


def test_bulk_convert_skips_existing_unless_overwrite(tmp_path: Path):
    source = tmp_path / "in"
    source.mkdir()
    (source / "ep.srt").write_text(VALID_SRT)
    destination = tmp_path / "out"

    first = bulk_convert(str(source), str(destination))
    assert len(first.converted) == 1

    second = bulk_convert(str(source), str(destination))
    assert second.converted == []
    assert len(second.skipped) == 1

    third = bulk_convert(str(source), str(destination), overwrite=True)
    assert len(third.converted) == 1
    assert third.skipped == []


def test_bulk_convert_dry_run_writes_nothing(tmp_path: Path):
    source = tmp_path / "in"
    source.mkdir()
    (source / "ep.srt").write_text(VALID_SRT)
    destination = tmp_path / "out"

    summary = bulk_convert(str(source), str(destination), dry_run=True)

    assert summary.dry_run
    assert len(summary.converted) == 1
    assert not destination.exists()


def test_bulk_convert_duplicate_sources_do_not_crash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    source = tmp_path / "in"
    source.mkdir()
    transcript = source / "ep.srt"
    transcript.write_text(VALID_SRT)
    destination = tmp_path / "out"

    def duplicate_list_files(directory: str, ignore: list[str]) -> list[str]:
        assert directory == str(source)
        assert ignore == []
        return [str(transcript), str(transcript)]

    monkeypatch.setattr(
        convert_module,
        "list_files",
        duplicate_list_files,
    )

    summary = convert_module.bulk_convert(str(source), str(destination), dry_run=True)

    assert [src for src, _ in summary.converted] == [
        str(transcript),
        str(transcript),
    ]


def test_bulk_convert_ignore_list(tmp_path: Path):
    source = tmp_path / "in"
    source.mkdir()
    (source / "ep.srt").write_text(VALID_SRT)
    (source / "skipme.srt").write_text(VALID_SRT)
    destination = tmp_path / "out"

    summary = bulk_convert(str(source), str(destination), ignore=["skipme.srt"])

    assert [src for src, _ in summary.converted] == [str(source / "ep.srt")]

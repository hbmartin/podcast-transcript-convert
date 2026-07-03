from pathlib import Path

from podcast_transcript_convert.file_typing import (
    FileType,
    _extract_file_type_from_first_line,
    _extract_file_type_from_name,
    identify_file_type,
    identify_file_types,
)


def test_extract_file_type_from_name():
    assert _extract_file_type_from_name("a/b.vtt") == FileType.VTT
    assert _extract_file_type_from_name("a/b.srt") == FileType.SRT
    assert _extract_file_type_from_name("a/b.HTML") == FileType.HTML
    assert _extract_file_type_from_name("a/b.htm") == FileType.HTML
    assert _extract_file_type_from_name("a/b.json") == FileType.JSON
    assert _extract_file_type_from_name("a/b.xml") == FileType.XML
    assert _extract_file_type_from_name("a/b.xsl") == FileType.XML
    assert _extract_file_type_from_name("a/b.txt") == FileType.UNKNOWN
    assert _extract_file_type_from_name("a/b") == FileType.UNKNOWN


def test_extract_file_type_from_first_line():
    assert _extract_file_type_from_first_line("WEBVTT\n") == FileType.VTT
    assert _extract_file_type_from_first_line("1\n") == FileType.SRT
    assert (
        _extract_file_type_from_first_line("00:00:00,000 --> 00:00:01,000\n")
        == FileType.SRT
    )
    assert _extract_file_type_from_first_line("<!DOCTYPE html>\n") == FileType.HTML
    assert _extract_file_type_from_first_line('<?xml version="1.0"?>') == FileType.XML
    assert _extract_file_type_from_first_line('{"version": "1.0.0"}') == FileType.JSON
    assert _extract_file_type_from_first_line("hello there") == FileType.UNKNOWN


def test_extract_file_type_from_first_line_empty_line_does_not_crash():
    assert _extract_file_type_from_first_line("") == FileType.UNKNOWN
    assert _extract_file_type_from_first_line("\n") == FileType.UNKNOWN
    assert _extract_file_type_from_first_line("   \n") == FileType.UNKNOWN


def test_identify_file_type_from_content(tmp_path: Path):
    vtt = tmp_path / "no_extension_vtt"
    vtt.write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nhi\n")
    assert identify_file_type(str(vtt)) == FileType.VTT


def test_identify_file_types_uses_content_for_unknown_extensions(tmp_path: Path):
    """Regression test: content-detected files must be filed under their type."""
    vtt = tmp_path / "transcript.txt"
    vtt.write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nhi\n")
    srt = tmp_path / "episode.subtitle"
    srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nhi\n\n")
    mystery = tmp_path / "mystery.bin"
    mystery.write_text("no transcript here")
    empty = tmp_path / "empty.dat"
    empty.write_text("")

    grouped = identify_file_types(
        [str(vtt), str(srt), str(mystery), str(empty)],
    )

    assert grouped[FileType.VTT] == [str(vtt)]
    assert grouped[FileType.SRT] == [str(srt)]
    assert sorted(grouped[FileType.UNKNOWN]) == sorted([str(mystery), str(empty)])


def test_identify_file_types_unreadable_file_is_unknown(tmp_path: Path):
    missing = tmp_path / "gone.txt"
    grouped = identify_file_types([str(missing)])
    assert grouped[FileType.UNKNOWN] == [str(missing)]

from pathlib import Path

from podcast_transcript_convert.file_utils import (
    _is_file_allowed,
    _read_first_line,
    list_files,
    map_files_in_parallel,
    read_text_robust,
)


def test_is_file_allowed():
    assert _is_file_allowed("a.srt", [])
    assert not _is_file_allowed("a.srt", ["a.srt"])
    assert not _is_file_allowed(".hidden", [])
    assert not _is_file_allowed("doc.pdf", [])
    assert not _is_file_allowed("blob.octet-stream", [])


def test_list_files(tmp_path: Path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.srt").write_text("x")
    (tmp_path / "sub" / "b.vtt").write_text("x")
    (tmp_path / ".hidden").write_text("x")
    (tmp_path / "skip.pdf").write_text("x")
    (tmp_path / "ignored.srt").write_text("x")

    files = list_files(str(tmp_path), ignore=["ignored.srt"])

    assert sorted(files) == sorted(
        [str(tmp_path / "a.srt"), str(tmp_path / "sub" / "b.vtt")],
    )


def test_read_text_robust_utf8_bom(tmp_path: Path):
    file = tmp_path / "bom.srt"
    file.write_bytes(b"\xef\xbb\xbfWEBVTT\n")
    assert read_text_robust(file) == "WEBVTT\n"


def test_read_text_robust_invalid_utf8(tmp_path: Path):
    file = tmp_path / "latin1.srt"
    file.write_bytes(b"caf\xe9 time\n")
    content = read_text_robust(file)
    assert content == "caf� time\n"


def test_read_first_line_invalid_utf8(tmp_path: Path):
    file = tmp_path / "latin1.srt"
    file.write_bytes(b"caf\xe9 time\nsecond line\n")
    assert _read_first_line(str(file)) == "caf� time\n"


def test_map_files_in_parallel_preserves_order(tmp_path: Path):
    paths = []
    for index in range(5):
        file = tmp_path / f"{index}.txt"
        file.write_text(str(index))
        paths.append(str(file))

    results = map_files_in_parallel(paths, lambda p: Path(p).read_text())

    assert results == [(path, Path(path).read_text()) for path in paths]

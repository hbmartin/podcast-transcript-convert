from podcast_transcript_convert.errors import (
    InvalidHtmlError,
    InvalidJsonError,
    InvalidSrtError,
    InvalidVttError,
    InvalidXmlError,
    NoStartTimeError,
    NoTranscriptFoundError,
    TranscriptConversionError,
    UnknownFileTypeError,
)


def test_all_errors_are_transcript_conversion_errors():
    for error in (
        InvalidHtmlError(),
        InvalidJsonError(),
        InvalidXmlError(),
        NoTranscriptFoundError(),
        InvalidSrtError("bad block"),
        InvalidVttError(),
        NoStartTimeError(),
        UnknownFileTypeError("a/b.bin"),
    ):
        assert isinstance(error, TranscriptConversionError)
        assert isinstance(error, ValueError)
        assert str(error)


def test_invalid_xml_error_message():
    assert "XML" in InvalidXmlError().message


def test_invalid_json_error_message():
    assert "JSON" in InvalidJsonError().message


def test_no_transcript_found_error_message():
    assert "transcript" in NoTranscriptFoundError().message


def test_invalid_srt_error_keeps_block():
    error = InvalidSrtError("00:00 --> nonsense")
    assert error.block == "00:00 --> nonsense"
    assert "00:00 --> nonsense" in str(error)


def test_unknown_file_type_error_keeps_path():
    error = UnknownFileTypeError("a/b.bin")
    assert error.file_path == "a/b.bin"
    assert "a/b.bin" in str(error)

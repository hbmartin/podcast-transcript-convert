"""Property-based tests for the timestamp parsers and speaker splitting."""

from hypothesis import given
from hypothesis import strategies as st

from podcast_transcript_convert.converters.html_to_json import _ts_to_secs
from podcast_transcript_convert.converters.srt_to_json import _mts_to_secs_float
from podcast_transcript_convert.models import split_speaker_prefix


@given(
    hours=st.integers(min_value=0, max_value=99),
    minutes=st.integers(min_value=0, max_value=59),
    seconds=st.integers(min_value=0, max_value=59),
    milliseconds=st.integers(min_value=0, max_value=999),
)
def test_mts_to_secs_float(hours: int, minutes: int, seconds: int, milliseconds: int):
    expected = round(
        hours * 3600 + minutes * 60 + seconds + milliseconds / 1000,
        3,
    )
    comma = f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    period = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    assert _mts_to_secs_float(comma) == expected
    assert _mts_to_secs_float(period) == expected


@given(
    hours=st.integers(min_value=0, max_value=99),
    minutes=st.integers(min_value=0, max_value=59),
    seconds=st.integers(min_value=0, max_value=59),
)
def test_ts_to_secs(hours: int, minutes: int, seconds: int):
    assert _ts_to_secs(f"{minutes}:{seconds:02d}") == minutes * 60 + seconds
    assert (
        _ts_to_secs(f"{hours}:{minutes:02d}:{seconds:02d}")
        == hours * 3600 + minutes * 60 + seconds
    )


@given(body=st.text(max_size=200))
def test_split_speaker_prefix_never_crashes(body: str):
    speaker, remainder = split_speaker_prefix(body)
    assert body.endswith(remainder)
    if speaker is not None:
        assert body.startswith(speaker)
        assert speaker == speaker.strip()

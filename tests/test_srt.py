from pathlib import Path

import pytest

from podcast_transcript_convert.converters.srt_to_json import (
    _mts_to_secs_float,
    srt_to_podcast_dict,
)
from podcast_transcript_convert.errors import InvalidSrtError


def test__mts_to_secs_float():
    assert _mts_to_secs_float("00:00:00,0") == 0
    assert _mts_to_secs_float("00:01:31,123") == 91.123
    assert _mts_to_secs_float("23:59:59,999") == 86399.999
    assert _mts_to_secs_float("02:01:31,0") == 7291
    with pytest.raises(ValueError):
        _mts_to_secs_float("abc")
    with pytest.raises(ValueError):
        _mts_to_secs_float("")


def test_srt_to_podcast_dict():
    srt_string = Path("tests/fixtures/Bloat.srt").read_text()
    transcript_dict = srt_to_podcast_dict(srt_string)
    assert transcript_dict["version"] == "1.0.0"
    assert len(transcript_dict["segments"]) == 724
    assert (
        transcript_dict["segments"][0]["body"]
        == "Michael: Hello, and welcome to PostgresFM, a weekly show about"
    )
    assert transcript_dict["segments"][0]["startTime"] == 0.060
    assert transcript_dict["segments"][0]["endTime"] == 2.680
    assert transcript_dict["segments"][-1]["body"] == "Take care, Chelsea."
    assert transcript_dict["segments"][-1]["startTime"] == 2173.940
    assert transcript_dict["segments"][-1]["endTime"] == 2174.920


def test_srt_to_podcast_dict_with_extra_whitespace():
    srt_string = Path("tests/fixtures/I Quit My Job.srt").read_text()
    transcript_dict = srt_to_podcast_dict(srt_string)
    assert (
        transcript_dict["segments"][0]["body"]
        == "Welcome to another episode of the map escaping podcast."
    )
    assert transcript_dict["segments"][-1]["body"] == "Bye."


def test_srt_to_podcast_dict_with_missing_whitespace():
    srt_string = Path("tests/fixtures/AI Autocomplete for QGIS.srt").read_text()
    transcript_dict = srt_to_podcast_dict(srt_string)
    assert transcript_dict["segments"][0]["body"] == "Hi,Brendan.Welcometothepodcast."
    assert transcript_dict["segments"][-1]["body"] == "Thanks."


def test_srt_to_podcast_dict_with_period_ts():
    srt_string = Path("tests/fixtures/Episode 17.srt").read_text()
    transcript_dict = srt_to_podcast_dict(srt_string)
    assert transcript_dict["segments"][0]["endTime"] == 5.0
    assert (
        transcript_dict["segments"][0]["body"]
        == "I think in terms of news, what would be great to kick off with is Swift Server."
    )
    assert transcript_dict["segments"][-1]["endTime"] == 2882.360
    assert transcript_dict["segments"][-1]["body"] == "Yeah."


def test_srt_to_podcast_dict_with_newlines_in_body():
    srt_string = Path("tests/fixtures/Yak Shaving with Tim Mitra.srt").read_text()
    transcript_dict = srt_to_podcast_dict(srt_string)
    assert (
        transcript_dict["segments"][0]["body"]
        == "Leo Dion (host): Before we begin today's episode, I wanted to let you know Bright Digit needs your help."
    )
    assert transcript_dict["segments"][881]["body"] == "?   Yeah."
    assert transcript_dict["segments"][-1]["body"] == "Bye everyone."


def test_srt_to_podcast_dict_invalid():
    with pytest.raises(InvalidSrtError):
        srt_to_podcast_dict("whatever")

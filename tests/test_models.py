from podcast_transcript_convert.models import (
    Segment,
    Transcript,
    split_speaker_prefix,
)


def test_split_speaker_prefix():
    assert split_speaker_prefix("Michael: Hello there") == ("Michael", "Hello there")
    assert split_speaker_prefix("Leo Dion (host): Before we begin") == (
        "Leo Dion (host)",
        "Before we begin",
    )
    assert split_speaker_prefix("Dr. Smith: Hi") == ("Dr. Smith", "Hi")


def test_split_speaker_prefix_no_match():
    assert split_speaker_prefix("Hello there") == (None, "Hello there")
    assert split_speaker_prefix("lowercase: nope") == (None, "lowercase: nope")
    assert split_speaker_prefix("Michael:no space") == (None, "Michael:no space")
    assert split_speaker_prefix("") == (None, "")
    assert split_speaker_prefix("A" * 80 + ": too long") == (
        None,
        "A" * 80 + ": too long",
    )


def test_segment_to_dict_omits_unset_fields():
    assert Segment().to_dict() == {}
    assert Segment(body="hi").to_dict() == {"body": "hi"}
    assert Segment(body="", start_time=0.0).to_dict() == {
        "startTime": 0.0,
        "body": "",
    }
    assert Segment(
        body="hi",
        start_time=1.0,
        end_time=2.0,
        speaker="Ann",
    ).to_dict() == {
        "speaker": "Ann",
        "startTime": 1.0,
        "endTime": 2.0,
        "body": "hi",
    }


def test_transcript_to_dict():
    transcript = Transcript(segments=[Segment(body="hi")])
    assert transcript.to_dict() == {
        "version": "1.0.0",
        "segments": [{"body": "hi"}],
    }


def test_transcript_to_dict_with_metadata():
    transcript = Transcript(
        segments=[Segment(body="hi")],
        metadata={"title": "Episode 1"},
    )
    assert transcript.to_dict()["metadata"] == {"title": "Episode 1"}

"""Dataclasses modeling the PodcastIndex transcript JSON format.

See the spec at:
https://github.com/Podcastindex-org/podcast-namespace/blob/main/transcripts/transcripts.md
"""

import re
from dataclasses import dataclass, field

SPEC_VERSION = "1.0.0"

# A leading "Speaker Name:" prefix, e.g. "Michael: Hello" or
# "Leo Dion (host): Before we begin". The name must start with an uppercase
# letter, be reasonably short, and be followed by a colon and whitespace.
_speaker_prefix = re.compile(
    r"^([A-Z][A-Za-z0-9 .\-'()&]{0,62}):\s+(\S.*)$",
    flags=re.DOTALL,
)


def split_speaker_prefix(body: str) -> tuple[str | None, str]:
    """Split a leading "Speaker Name:" prefix from a segment body.

    Returns a (speaker, body) tuple; speaker is None when no prefix is found.
    """
    if match := _speaker_prefix.match(body):
        return match[1].strip(), match[2]
    return None, body


@dataclass(slots=True)
class Segment:
    """A single transcript segment (one cue/utterance)."""

    body: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    speaker: str | None = None

    def to_dict(self) -> dict[str, str | float]:
        """Serialize to a PodcastIndex JSON segment dict, omitting unset fields."""
        segment: dict[str, str | float] = {}
        if self.speaker is not None:
            segment["speaker"] = self.speaker
        if self.start_time is not None:
            segment["startTime"] = self.start_time
        if self.end_time is not None:
            segment["endTime"] = self.end_time
        if self.body is not None:
            segment["body"] = self.body
        return segment


@dataclass(slots=True)
class Transcript:
    """A full transcript: a list of segments plus optional feed metadata."""

    segments: list[Segment] = field(default_factory=list)
    metadata: dict | None = None
    version: str = SPEC_VERSION

    def to_dict(self) -> dict:
        """Serialize to a PodcastIndex JSON transcript dict."""
        transcript: dict = {
            "version": self.version,
            "segments": [segment.to_dict() for segment in self.segments],
        }
        if self.metadata:
            transcript["metadata"] = self.metadata
        return transcript

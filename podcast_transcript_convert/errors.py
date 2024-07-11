class TranscriptConversionError(ValueError):
    """Base class for exceptions raised during transcript conversion."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidHtmlError(TranscriptConversionError):
    """The HTML does not conform to the expected format of a valid transcript.

    Specifically, when there are no <cite> or <time> tags in the file.
    """

    def __init__(self) -> None:
        super().__init__("The provided HTML file is not a valid transcript.")


class InvalidXmlError(TranscriptConversionError):
    """The XML does not conform to http://podlove.org/simple-transcripts ."""

    def __init__(self) -> None:
        super().__init__("The provided XML file is not a valid transcript.")


class NoTranscriptFoundError(TranscriptConversionError):
    """Failed to locate transcript blocks in the provided source.

    This may happen for an invalid or empty file.
    """

    def __init__(self) -> None:
        super().__init__(
            "The provided source does not contain a transcript or could not be parsed.",
        )


class InvalidSrtError(TranscriptConversionError):
    """Failed to parse transcript blocks in the SRT."""

    def __init__(self, block: str) -> None:
        self.block = block
        super().__init__(f"The provided SRT could not be parsed:\n{block}")


class InvalidVttError(TranscriptConversionError):
    """Failed to parse WebVTT."""

    def __init__(self) -> None:
        super().__init__("The provided VTT could not be parsed.")


class NoStartTimeError(TranscriptConversionError):
    """Failed to find startTime in source transcript."""

    def __init__(self) -> None:
        super().__init__("Failed to find startTime in source transcript.")


class UnknownFileTypeError(TranscriptConversionError):
    """Failed to determine the file type."""

    def __init__(self, file_path: str) -> None:
        super().__init__(f"Failed to determine the file type of {file_path}.")
        self.file_path = file_path

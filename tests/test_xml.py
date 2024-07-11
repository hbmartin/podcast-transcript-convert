from pathlib import Path

from podcast_transcript_convert.converters.xml_to_json import xml_to_podcast_dict


def test_xml_to_podcast_dict():
    html_string = Path(
        "tests/fixtures/Hunting CrossSite Scripting on the Web.xsl",
    ).read_text()
    transcript_dict = xml_to_podcast_dict(html_string)
    assert transcript_dict["segments"][0]["body"] == "Welcome to"
    assert transcript_dict["segments"][0]["startTime"] == 0.82
    assert transcript_dict["segments"][0]["endTime"] == 1.66
    assert (
        transcript_dict["segments"][-1]["body"]
        == """
thanks everyone out there who listened to "The Open Source Way". If you enjoyed this episode, please share it and don't miss the next one. We usually publish every last Wednesday of the month, and you'll find us on openSAP and in all those places where you find your other podcasts . Either the mainstream apps that you know, or some of the, themselves, open-source podcast apps. Thanks again and bye bye.
    """.strip()
    )
    assert transcript_dict["segments"][-1]["startTime"] == 1739.4
    assert transcript_dict["segments"][-1]["endTime"] == 1766.55

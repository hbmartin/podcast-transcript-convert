import sqlite3
from pathlib import Path

from podcast_transcript_convert.constants import (
    ENCLOSURE_URL,
    FEED_TITLE,
    GUID,
    TITLE,
    XML_URL,
)
from podcast_transcript_convert.database import list_files_from_db


def _create_db(db_path: Path) -> None:
    con = sqlite3.connect(db_path)
    con.executescript(
        """
        CREATE TABLE episodes_extended (
            transcriptDownloadPath TEXT,
            title TEXT,
            enclosureUrl TEXT,
            guid TEXT,
            feedXmlUrl TEXT
        );
        CREATE TABLE feeds_extended (
            title TEXT,
            xmlUrl TEXT
        );
        INSERT INTO feeds_extended VALUES
            ('My Show', 'https://example.com/feed.xml');
        INSERT INTO episodes_extended VALUES
            ('/transcripts/ep1.srt', 'Episode 1', 'https://example.com/ep1.mp3',
             'guid-1', 'https://example.com/feed.xml'),
            ('/transcripts/ignored.srt', 'Episode 2', 'https://example.com/ep2.mp3',
             'guid-2', 'https://example.com/feed.xml'),
            (NULL, 'No transcript', 'https://example.com/ep3.mp3',
             'guid-3', 'https://example.com/feed.xml');
        """,
    )
    con.commit()
    con.close()


def test_list_files_from_db(tmp_path: Path):
    db_path = tmp_path / "overcast.db"
    _create_db(db_path)

    files, metadatas = list_files_from_db(str(db_path), ignore=["ignored.srt"])

    assert files == ["/transcripts/ep1.srt"]
    metadata = metadatas["/transcripts/ep1.srt"]
    assert metadata[TITLE] == "Episode 1"
    assert metadata[ENCLOSURE_URL] == "https://example.com/ep1.mp3"
    assert metadata[GUID] == "guid-1"
    assert metadata[FEED_TITLE] == "My Show"
    assert metadata[XML_URL] == "https://example.com/feed.xml"

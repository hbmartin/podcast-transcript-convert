import sqlite3
from collections.abc import Iterable
from sqlite3 import Connection

from .constants import (
    ENCLOSURE_URL,
    EPISODES_EXTENDED,
    FEED_TITLE,
    FEED_XML_URL,
    FEEDS_EXTENDED,
    GUID,
    TITLE,
    TRANSCRIPT_DL_PATH,
    XML_URL,
)
from .file_utils import _is_file_allowed


def _to_file_and_metadata(
    row: tuple[str, str, str, str, str, str],
) -> tuple[str, dict[str, str]]:
    """Convert a row from the database to a file path and metadata."""
    transcript_path, title, url, guid, feed_title, feed_xml = row
    return (
        transcript_path,
        {
            ENCLOSURE_URL: url,
            GUID: guid,
            TITLE: title,
            FEED_TITLE: feed_title,
            XML_URL: feed_xml,
        },
    )


def _select_transcript_paths(con: Connection) -> Iterable[tuple[str, dict[str, str]]]:
    """Find episodes with transcripts to download.

    Yields (transcript path, episode title, episode url,
    episode guid, feed title, feed xml)
    """
    select = (
        f"SELECT {TRANSCRIPT_DL_PATH}, {EPISODES_EXTENDED}.{TITLE},  "
        f"{EPISODES_EXTENDED}.{ENCLOSURE_URL}, {EPISODES_EXTENDED}.{GUID}, "
        f"{FEEDS_EXTENDED}.{TITLE},  {FEEDS_EXTENDED}.{XML_URL} "
        f"FROM {EPISODES_EXTENDED} "
    )
    where = f"WHERE {TRANSCRIPT_DL_PATH} IS NOT NULL"
    query = (
        f"{select} LEFT JOIN {FEEDS_EXTENDED} "
        f"ON {EPISODES_EXTENDED}.{FEED_XML_URL} = {FEEDS_EXTENDED}.{XML_URL} "
        f"{where} "
    )

    yield from map(_to_file_and_metadata, con.cursor().execute(query))


def list_files_from_db(
    db_path: str,
    ignore: list[str],
) -> tuple[list[str], dict[str, dict[str, str]]]:
    """List files from a database."""
    files = []
    metadatas = {}

    with sqlite3.connect(db_path) as con:
        for file, data in _select_transcript_paths(con):
            if not _is_file_allowed(filename=file.split("/")[-1], ignore=ignore):
                continue
            files.append(file)
            metadatas[file] = data

    return files, metadatas

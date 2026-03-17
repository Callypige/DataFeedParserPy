import argparse
import logging
import sqlite3
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


# Constants
DB_PATH = Path("epg.sqlite")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_time(raw: str) -> datetime:
    """Parse '20260317024000 +0000' → datetime."""
    return datetime.strptime(raw.strip(), "%Y%m%d%H%M%S %z")


# Fetch
def fetch_xml(url: str) -> str:
    """Download the EPG XML file from the remote server."""
    logger.info("Fetching EPG from %s", url)

    # Fetch the XML data
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        logger.error("Failed to fetch EPG: %s", e)
        raise

    logger.info("EPG fetched successfully")
    return xml_data


def parse_xml(xml_data: str) -> list[dict]:
    """Parse the EPG XML and return a list of programs."""
    logger.info("Parsing XML...")

    # Parse the XML data
    root = ET.fromstring(xml_data)
    programs = []

    for programme in root.findall("programme"):
        start = parse_time(programme.get("start", ""))
        stop = parse_time(programme.get("stop", ""))

        programs.append({
            "channel":     programme.get("channel", ""),
            "start_time":  parse_time(programme.get("start", "")),
            "stop_time":   parse_time(programme.get("stop", "")),
            "duration":    int((stop - start).total_seconds()),
            "title":       programme.findtext("title", ""),
            "description": programme.findtext("desc"),
        })

    logger.info("Parsed %d programs", len(programs))
    return programs


def init_db(conn: sqlite3.Connection) -> None:
    """Create the database tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS program (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT,
            start_time DATETIME,
            stop_time DATETIME,
            title TEXT,
            description TEXT,
            UNIQUE(start_time, title)
        );
    """)
    conn.commit()
    logger.info("Database initialized")


def store_db(conn: sqlite3.Connection, programs: list[dict]) -> None:
    """Store the programs and their castings in the database."""
    logger.info("Storing programs in the database...")

    values = [
        (
            program["channel"],
            program["start_time"].isoformat(),
            program["stop_time"].isoformat(),
            program["title"],
            program["description"],
        )
        for program in programs
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO program (channel, start_time, stop_time,
         title, description) VALUES (?, ?, ?, ?, ?)
    """, values)

    conn.commit()

    logger.info("Stored %d programs in the database", len(programs))


# argparse file
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and store an EPG feed")
    parser.add_argument("url", help="URL of the EPG feed (XML or JSON)")
    return parser.parse_args()


# fetch_xml and parse_xml functions and database functions
def main() -> None:
    """Main function."""
    xml_data = fetch_xml(parse_args().url)
    programs = parse_xml(xml_data)

    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        store_db(conn, programs)

    logger.info("Done!")


if __name__ == "__main__":
    main()

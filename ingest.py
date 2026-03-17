import logging
import sqlite3
import ssl
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Constants
EPG_URL = "https://testepg.r0ro.fr/epg.xml"
CA_CERT = Path("ca.crt")
DB_PATH = Path("epg.sqlite")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# Fetch
def fetch_xml() -> str:
    """Download the EPG XML file from the remote server."""
    logger.info("Fetching EPG from %s", EPG_URL)

    # Create SSL context with CA certificate
    if not CA_CERT.exists():
        logger.error("CA certificate not found at %s", CA_CERT)
        raise FileNotFoundError(f"CA certificate not found at {CA_CERT}")

    ssl_context = ssl.create_default_context(cafile=CA_CERT)

    # Fetch the XML data
    try:
        with urllib.request.urlopen(EPG_URL, context=ssl_context) as response:
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

    # The diff between "get" and "findtext"
    # is that get returns None if the element is not found,
    #  while findtext returns a default value (empty string in this case)
    for programme in root.findall("program"):
        programs.append({
            "start_time": datetime.fromisoformat(
                programme.get("start_time", "")
            ),
            "title": programme.findtext("title", ""),
            "subtitle": programme.findtext("subtitle", ""),
            "duration": int(programme.findtext("duration", "0")),
            "type": programme.findtext("type", ""),
            "description": programme.findtext("description", ""),
            "persons": [
                {
                    "firstname": person.get("firstname", ""),
                    "lastname": person.get("lastname", ""),
                    "function": person.get("function", ""),
                }
                for person in programme.findall("casting/person")
            ],
        })

    logger.info("Parsed %d programs", len(programs))
    return programs


def init_db(conn: sqlite3.Connection) -> None:
    """Create the database tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS program (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time DATETIME,
            title TEXT,
            subtitle TEXT,
            duration INTEGER,
            type TEXT,
            description TEXT,
            UNIQUE(start_time, title)
        );
        CREATE TABLE IF NOT EXISTS person (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT,
            lastname TEXT,
            UNIQUE(firstname, lastname)
        );
        CREATE TABLE IF NOT EXISTS casting (
            personid INTEGER,
            programid INTEGER,
            function TEXT,
            UNIQUE(personid, programid, function)
        );
    """)
    conn.commit()
    logger.info("Database initialized")


def get_or_create_person(conn: sqlite3.Connection, person: dict) -> int:
    """Get existing person id or create a new one.
    Returns the person id.
    """
    existing = conn.execute(
        "SELECT id FROM person WHERE firstname=? AND lastname=?",
        (person["firstname"], person["lastname"]),
    ).fetchone()

    if existing:
        return existing[0]

    # if person doesn't exist, create it
    cursor = conn.execute(
        "INSERT INTO person (firstname, lastname) VALUES (?, ?)",
        (person["firstname"], person["lastname"]),
    )
    return cursor.lastrowid or 0


def get_or_create_program(conn: sqlite3.Connection, program: dict) -> int:
    """Get existing programm id or create a new one
    Returns the program id.
    """
    existing = conn.execute(
        "SELECT id FROM program WHERE start_time=? AND title=?",
        (program["start_time"].isoformat(), program["title"])
    ).fetchone()

    if existing:
        return existing[0]

    # if program doesn't exist, create it
    cursor = conn.execute(
        "INSERT INTO program "
        "(start_time, title, subtitle, duration, type, description) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            program["start_time"].isoformat(),
            program["title"],
            program["subtitle"],
            program["duration"],
            program["type"],
            program["description"]
        )
    )
    return cursor.lastrowid or 0


def store_db(conn: sqlite3.Connection, programs: list[dict]) -> None:
    """Store the programs and their castings in the database."""
    for program in programs:
        program_id = get_or_create_program(conn, program)

        # Store the castings for each program
        # After getting the program_id,
        # we loop through the persons in the program
        for person in program["persons"]:
            person_id = get_or_create_person(conn, person)
            # Then we insert a row in the casting table
            # with the person_id, program_id, and function
            conn.execute(
                "INSERT INTO casting "
                "(personid, programid, function) VALUES (?, ?, ?)",
                (person_id, program_id, person["function"])
            )

    conn.commit()
    logger.info("Programs stored in database successfully")


# fetch_xml and parse_xml functions and database functions
def main() -> None:
    """Main function."""
    xml_data = fetch_xml()
    programs = parse_xml(xml_data)

    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        store_db(conn, programs)

    logger.info("Done!")


if __name__ == "__main__":
    main()

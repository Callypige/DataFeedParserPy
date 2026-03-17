import datetime
import json
import sqlite3

from ingest import get_or_create_person, get_or_create_program

json_data = '''{
    "programs": [
        {
            "start_time": "2019-05-16T05:22:00+02:00",
            "title": "Le Journal",
            "duration": 180,
            "subtitle": null,
            "type": "Magazine",
            "description": "Une description.",
            "casting": [
                {
                    "firstname": "Monique",
                    "lastname": "Atlan",
                    "function": "Présentateur"
                }
            ]
        }
    ]
}'''


def parse_json(json_data: str) -> list[dict]:
    """Parse the JSON data and return a program dictionary."""
    data = json.loads(json_data)

    programs = []

    for program in data.get("programs", []):
        programs.append({
            "start_time": datetime.datetime.fromisoformat(
                program.get("start_time", "")
            ),
            "title": program.get("title", ""),
            "subtitle": program.get("subtitle", ""),
            "duration": int(program.get("duration", 0)),
            "type": program.get("type", ""),
            "description": program.get("description", ""),
            "persons": [
                {
                    "firstname": person.get("firstname", ""),
                    "lastname": person.get("lastname", ""),
                    "function": person.get("function", ""),
                }
                for person in program.get("casting", [])
            ],
        })

    return programs


def create_db(conn: sqlite3.Connection) -> None:
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
            program_id INTEGER,
            person_id INTEGER,
            function TEXT,
            UNIQUE(program_id, person_id)
        );
    """)


def store_db(conn: sqlite3.Connection, programs: list[dict]) -> None:
    """Store the program data in the database."""
    try:
        for program in programs:
            program_id = get_or_create_program(conn, program)
            for person in program["persons"]:
                person_id = get_or_create_person(conn, person)
                conn.execute(
                    "INSERT OR IGNORE INTO casting "
                    "(program_id, person_id) VALUES (?, ?)",
                    (program_id, person_id)
                )
        conn.commit()
    except Exception as e:
        print("Error storing data in database:", e)
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        programs = parse_json(json_data)
        conn = sqlite3.connect("test.db")
        create_db(conn)
        store_db(conn, programs)

    except Exception as e:
        print("Error parsing JSON:", e)

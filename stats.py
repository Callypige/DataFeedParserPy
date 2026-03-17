import sqlite3
from pathlib import Path

DB_PATH = Path("epg.sqlite")


def get_connection() -> sqlite3.Connection:
    """Open a connection to the database."""
    return sqlite3.connect(DB_PATH)


def stat_1(conn: sqlite3.Connection) -> int:
    """Return the count of programs with duration >= 10 minutes.
    (600 seconds)
    """
    row = conn.execute(
        "SELECT COUNT(*) FROM program WHERE duration >= 600"
    ).fetchone()
    print(f"1. Programs >= 10 minutes: {row[0]}")
    return row[0]


def stat_2(conn: sqlite3.Connection) -> tuple:
    """Return the start time and title of the longest program on 2019-05-18."""
    row = conn.execute("""
        SELECT start_time, title FROM program
        WHERE start_time LIKE '2019-05-18%'
        ORDER BY duration DESC LIMIT 1
    """).fetchone()
    print(f"2. Longest program on 2019-05-18: {row[0]} — {row[1]}")
    return row


def stat_3(conn: sqlite3.Connection) -> list:
    """Return the top 5 Présentateurs with the most appearances."""
    rows = conn.execute("""
        SELECT p.firstname, p.lastname, COUNT(*) as total
        FROM person p
        JOIN casting c ON c.personid = p.id
        WHERE c.function = 'Présentateur'
        GROUP BY p.id ORDER BY total DESC LIMIT 5
    """).fetchall()
    print("3. Top 5 Présentateurs:")
    for row in rows:
        print(f"   {row[0]} {row[1]} — {row[2]} programs")
    return rows


def stat_4(conn: sqlite3.Connection) -> list:
    """Return the list of programs with 'Manuel Blanc'."""
    rows = conn.execute("""
        SELECT pr.start_time, pr.title FROM program pr
        JOIN casting c ON c.programid = pr.id
        JOIN person p ON p.id = c.personid
        WHERE p.firstname = 'Manuel' AND p.lastname = 'Blanc'
    """).fetchall()
    print("4. Programs with Manuel Blanc:")
    for row in rows:
        print(f"   {row[0]} — {row[1]}")
    print(f"   Total: {len(rows)} programs")
    return rows


# List of all stats functions to run
STATS = [stat_1, stat_2, stat_3, stat_4]


def main() -> None:
    with get_connection() as conn:
        # Run all stats and print results
        for stat in STATS:
            stat(conn)
            print("-" * 50)


if __name__ == "__main__":
    main()

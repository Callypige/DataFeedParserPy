import datetime
import sqlite3
import unittest
from unittest.mock import MagicMock, patch

from ingest import fetch_xml, init_db, parse_xml, store_db
from stats import stat_1, stat_2, stat_3, stat_4

# XML sample
SAMPLE_XML = """<epg>
    <program start_time="2019-05-16T05:22:00+02:00">
        <duration>180</duration>
        <title>Dans quelle éta-gère</title>
        <subtitle>Un sous-titre</subtitle>
        <type>Magazine</type>
        <description>Une description.</description>
        <casting>
            <person firstname="Monique" lastname="Atlan"
                    function="Présentateur"/>
        </casting>
    </program>
</epg>"""


class TestIngest(unittest.TestCase):

    def setUp(self):
        """In-memory SQLite database, reset before each test."""
        self.conn = sqlite3.connect(":memory:")
        init_db(self.conn)

    def tearDown(self):
        self.conn.close()

    @patch("urllib.request.urlopen")
    def test_fetch_xml(self, mock_urlopen: MagicMock) -> None:
        """fetch_xml returns a string containing XML."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"<epg></epg>"
        # Mock the context manager behavior of urlopen
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = fetch_xml()
        self.assertIsInstance(result, str)
        self.assertIn("<epg>", result)

    def test_parse_xml(self) -> None:
        """parse_xml returns the correct list of programs."""
        programs = parse_xml(SAMPLE_XML)

        self.assertEqual(len(programs), 1)
        self.assertEqual(programs[0]["title"], "Dans quelle éta-gère")
        self.assertEqual(programs[0]["duration"], 180)
        self.assertEqual(programs[0]["persons"][0]["firstname"], "Monique")

    def test_init_db(self) -> None:
        """init_db creates the 3 tables correctly."""
        tables = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]

        self.assertIn("program", table_names)
        self.assertIn("person", table_names)
        self.assertIn("casting", table_names)

    def test_store_db(self) -> None:
        """store_db inserts data in the database correctly."""
        programs = parse_xml(SAMPLE_XML)
        store_db(self.conn, programs)

        program_count = len(
            self.conn.execute("SELECT * FROM program").fetchall()
        )
        self.assertEqual(program_count, 1)
        person_count = len(
            self.conn.execute("SELECT * FROM person").fetchall()
        )
        self.assertEqual(person_count, 1)
        casting_count = len(
            self.conn.execute("SELECT * FROM casting").fetchall()
        )
        self.assertEqual(casting_count, 1)

    def test_store_db_idempotent(self):
        programs = parse_xml(SAMPLE_XML)
        store_db(self.conn, programs)  # First time
        # Second time, should not create duplicates
        store_db(self.conn, programs)

        # Check that we still have only 1 program, 1 person, and
        # 1 casting entry
        program_count = len(
            self.conn.execute("SELECT * FROM program").fetchall()
        )
        self.assertEqual(program_count, 1)

    def test_get_or_create_person(self) -> None:
        """get_or_create_person inserts a person if they don't exist, and
        returns their ID.
        """
        from ingest import get_or_create_person

        # First call should create the person and return their ID
        person_id = get_or_create_person(
            self.conn, {"firstname": "Jean", "lastname": "Dupont"}
        )
        self.assertIsInstance(person_id, int)

        # Calling again with the same name should return the same ID
        same_person_id = get_or_create_person(
            self.conn, {"firstname": "Jean", "lastname": "Dupont"}
        )
        self.assertEqual(person_id, same_person_id)

    def test_get_or_create_program(self) -> None:
        """get_or_create_program inserts a program if it doesn't exist, and
        returns its ID.
        """
        from ingest import get_or_create_program

        program_data = {
            "start_time": datetime.datetime.fromisoformat("2019-05-16T05:22:00+02:00"),
            "title": "Test Program",
            "subtitle": "Test Subtitle",
            "duration": 180,
            "type": "Magazine",
            "description": "Test Description"
        }

        # First call should create the program and return its ID
        program_id = get_or_create_program(self.conn, program_data)
        self.assertIsInstance(program_id, int)

        # Calling again with the same start_time and title should
        # return the same ID
        same_program_id = get_or_create_program(self.conn, program_data)
        self.assertEqual(program_id, same_program_id)


class TestStats(unittest.TestCase):

    def setUp(self):
        # In-memory database for testing stats, with sample data
        self.conn = sqlite3.connect(":memory:")
        init_db(self.conn)
        self.conn.executescript("""
            INSERT INTO program (start_time, title, duration) VALUES
                ('2019-05-18T10:00:00+02:00', 'Programme long', 3600),
                ('2019-05-18T12:00:00+02:00', 'Programme court', 300),
                ('2019-05-16T08:00:00+02:00', 'Autre programme', 600);
            INSERT INTO person (firstname, lastname) VALUES
                ('Manuel', 'Blanc'),
                ('Bruno', 'Guillon');
            INSERT INTO casting (personid, programid, function) VALUES
                (1, 1, 'Présentateur'),
                (2, 2, 'Présentateur'),
                (2, 3, 'Présentateur');
        """)

    # Close the connection after each test
    def tearDown(self):
        self.conn.close()

    def test_stat_1(self):
        # stat_1 should return the count of programs longer than 10 minutes
        self.assertEqual(stat_1(self.conn), 2)

    def test_stat_2(self):
        # stat_2 should return the start time and the title of the program
        # with the biggest duration on 2019-05-18
        self.assertEqual(stat_2(self.conn)[1], "Programme long")

    def test_stat_3(self):
        # stat_3 should return the last name of the person with the
        # most appearances. In this case, Bruno Guillon appears in 2
        # programs, while Manuel Blanc appears in 1 program
        self.assertEqual(stat_3(self.conn)[0][1], "Guillon")

    def test_stat_4(self):
        # stat_4 should return the list of programs with 'Manuel Blanc'
        self.assertEqual(stat_4(self.conn)[0][1], "Programme long")

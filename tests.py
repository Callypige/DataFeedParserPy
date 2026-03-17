from datetime import datetime
import sqlite3
import unittest
from unittest.mock import MagicMock, patch

from ingest import fetch_xml, init_db, parse_xml, store_db

SAMPLE_XML = """<tv>
    <programme channel="55730" start="20260317024000 +0000" stop="20260317031000 +0000">
        <title lang="fr">Des volcans et des hommes</title>
        <desc>En Indonésie, les habitants vouent un culte au volcan Bromo.</desc>
        <date>2026-03-17</date>
    </programme>
</tv>"""


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
        mock_response.read.return_value = b"<tv></tv>"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = fetch_xml("https://fake-url.com/epg.xml")
        self.assertIsInstance(result, str)
        self.assertIn("<tv>", result)

    def test_parse_xml(self) -> None:
        """parse_xml returns the correct list of programs."""
        programs = parse_xml(SAMPLE_XML)

        self.assertEqual(len(programs), 1)
        self.assertEqual(programs[0]["title"], "Des volcans et des hommes")
        self.assertEqual(programs[0]["channel"], "55730")
        self.assertIsInstance(programs[0]["start_time"], datetime)
        self.assertIsInstance(programs[0]["duration"], int)

    def test_init_db(self) -> None:
        """init_db creates the program table correctly."""
        tables = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        self.assertIn("program", table_names)

    def test_store_db(self) -> None:
        """store_db inserts data in the database correctly."""
        programs = parse_xml(SAMPLE_XML)
        store_db(self.conn, programs)

        count = len(self.conn.execute("SELECT * FROM program").fetchall())
        self.assertEqual(count, 1)

    def test_store_db_idempotent(self) -> None:
        """store_db should not duplicate data when called twice."""
        programs = parse_xml(SAMPLE_XML)
        store_db(self.conn, programs)
        store_db(self.conn, programs)

        count = len(self.conn.execute("SELECT * FROM program").fetchall())
        self.assertEqual(count, 1)

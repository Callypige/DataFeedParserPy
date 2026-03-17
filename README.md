# DataFeedParserPy

A Python CLI tool that fetches an XML feed from a remote server, parses it and stores it into a SQLite database.

## Features

- Fetches XML feed over HTTPS with custom SSL certificate support
- Parses XML into structured data
- Stores data in a normalized SQLite database (3 tables)
- Idempotent ingestion — safe to run multiple times
- SQL statistics queries
- Unit tests with in-memory database and network mock

## Requirements

- Python 3.11+
- No external dependencies — stdlib only

## Installation
```bash
git clone https://github.com/Callypige/DataFeedParserPy.git
cd DataFeedParserPy
```

## Usage

### Ingest the feed
```bash
python ingest.py
```

### Run the stats
```bash
python stats.py
```

### Run the tests
```bash
python -m unittest tests.py
```

## Project structure
```
├── ingest.py   # Fetch, parse and store the XML feed
├── stats.py    # SQL queries on the database
├── tests.py    # Unit tests
└── ca.crt      # SSL certificate (required)
```

## Database schema
```
program (id, start_time, title, subtitle, duration, type, description)
person  (id, firstname, lastname)
casting (personid, programid, function)
```

## Notes

- `ca.crt` must be present in the root directory
- `epg.sqlite` is generated automatically on first run

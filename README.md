# DataFeedParserPy

A Python CLI tool that fetches an XML EPG feed from a remote server, parses it and stores it into a SQLite database.

## Features

- Fetches XML feed over HTTPS
- Parses XMLTV format into structured data
- Stores data in a SQLite database
- Idempotent ingestion — safe to run multiple times
- SQL statistics queries
- Unit tests with in-memory database and network mock
- No external dependencies — stdlib only

## Requirements

- Python 3.11+

## Installation
```bash
git clone https://github.com/Callypige/DataFeedParserPy.git
cd DataFeedParserPy
```

## Usage

### Ingest a feed
```bash
python ingest.py <url>
```

#### Example — Arte
```bash
python ingest.py "https://epg.pw/api/epg.xml?channel_id=55730"
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
└── tests.py    # Unit tests
```

## Database schema
```
program (id, channel, start_time, stop_time, duration, title, description)
```

## Notes

- `epg.sqlite` is generated automatically on first run
- Any XMLTV-compatible feed URL can be used
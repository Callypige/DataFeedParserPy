# Here, we put parsing xml and json files function
from asyncio.log import logger
import datetime
import json
import xml.etree.ElementTree as ET


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
            "start_time": datetime.datetime.fromisoformat(
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

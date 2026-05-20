import json
import logging
import os
import time

import schedule

from db import get_connection, init_db
from event import Events, broadcast_event, subscribe_to_event

iocs = []

def add_ioc(name, file_hash, poll_time=60):
    """
    Create a new IOC JSON file.

    The generated IOC matches the structure documented in the README:
        {
            "name": "...",
            "poll_time": <minutes>,
            "file_hash": "..."
        }
    """
    try:
        if not os.path.exists("ioc"):
            os.makedirs("ioc")

        ioc_payload = {
            "name": name,
            "poll_time": poll_time,
            "file_hash": file_hash,
        }

        with open("ioc/{name}.json".format(name=name), "w") as ioc_file:
            ioc_file.write(json.dumps(ioc_payload))

        return True
    except Exception as e:
        logging.exception(e)
        return False


def print_iocs(iocs):
    if len(iocs) > 0:
        print("[+] Loaded IOCs:")

        for ioc in iocs:
            name = ioc.get("name", "<unnamed>")
            print("\t - {name}".format(name=name))

        print("")


def _normalize_ioc(raw_ioc, filename):
    """
    Ensure the IOC has a name and poll_time.

    If these fields are missing, they are inferred from the filename
    or defaulted to sensible values.
    """
    ioc = dict(raw_ioc)
    if "name" not in ioc or not ioc["name"]:
        # Use the filename (without extension) as a fallback name.
        ioc["name"] = os.path.splitext(filename)[0]

    if "poll_time" not in ioc or not isinstance(ioc["poll_time"], int):
        ioc["poll_time"] = 60

    return ioc


def load_iocs():
    """
    Load IOCs from the JSON files in the `ioc` directory and mirror them
    into the SQLite database.
    """
    global iocs

    init_db()
    iocs = []

    # Ensure IOC directory exists so users can freely add JSON files.
    try:
        if not os.path.exists("ioc"):
            os.makedirs("ioc")
        files = os.listdir("ioc")
    except Exception as e:
        print("[!] Could not list IOC directory!")
        logging.exception(e)
        return iocs

    with get_connection() as conn:
        cursor = conn.cursor()

        for file in files:
            if not file.endswith(".json"):
                continue

            try:
                path = os.path.join("ioc", file)
                with open(path, "r") as ioc_file:
                    raw_ioc = json.loads(ioc_file.read())

                logging.info("Loaded IOC from {file}.".format(file=file))
                normalized = _normalize_ioc(raw_ioc, file)
                iocs.append(normalized)

                # Build metadata JSON by stripping well-known keys.
                metadata = dict(normalized)
                for key in ("name", "file_hash", "poll_time"):
                    metadata.pop(key, None)

                metadata_json = json.dumps(metadata) if metadata else None

                cursor.execute(
                    """
                    INSERT INTO iocs
                        (name, file_hash, poll_time, metadata_json, created_at_unix, active)
                    VALUES (?, ?, ?, ?, ?, 1)
                    ON CONFLICT(name) DO UPDATE SET
                        file_hash = excluded.file_hash,
                        poll_time = excluded.poll_time,
                        metadata_json = excluded.metadata_json
                    """,
                    (
                        normalized["name"],
                        normalized["file_hash"],
                        normalized["poll_time"],
                        metadata_json,
                        int(time.time()),
                    )
                )
            except Exception as e:
                print("[!] Could not load {ioc}".format(ioc=file))
                logging.exception(e)
                continue

        conn.commit()

    print_iocs(iocs)

    return iocs


def schedule_iocs():
    for ioc in iocs:
        schedule.every(ioc["poll_time"]).minutes.do(broadcast_event, Events.COLLECT, ioc)

    # Also hunt them manually once when initializing.
    hunt_iocs()

def hunt_iocs():
    for ioc in iocs:
        broadcast_event(Events.COLLECT, ioc)


subscribe_to_event(Events.INITIALIZE, load_iocs)

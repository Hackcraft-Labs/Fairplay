import json
import logging
import os
import time

from db import get_connection, init_db
from event import Events, broadcast_event, subscribe_to_event

DETECTIONS_FILE = "detections/detections.json"

# Kept as an in-memory cache for backward compatibility and potential
# future CLI use, but the canonical store is now SQLite.
detections = []

def _build_cache_from_db():
    """
    Populate the in-memory `detections` list from the SQLite database.

    This reconstructs the same structure that was previously stored
    in detections/detections.json so any existing consumers remain
    compatible.
    """
    global detections
    detections = []

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                d.id,
                d.name,
                d.file_hash,
                d.initial_detection_time_unix,
                d.initial_detection_time_text
            FROM detections d
            WHERE d.deleted = 0
            """
        )
        detection_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                ds.detection_id,
                ds.collector_name,
                ds.extra_info_json
            FROM detection_sources ds
            """
        )
        source_rows = cursor.fetchall()

        sources_by_detection_id = {}
        for row in source_rows:
            det_id = row["detection_id"]
            collector_name = row["collector_name"]
            extra_info_json = row["extra_info_json"]
            try:
                extra_info_list = json.loads(extra_info_json) if extra_info_json else []
            except Exception:
                extra_info_list = []

            if det_id not in sources_by_detection_id:
                sources_by_detection_id[det_id] = {
                    "sources": [],
                    "extra_info": {}
                }

            sources_by_detection_id[det_id]["sources"].append(collector_name)
            sources_by_detection_id[det_id]["extra_info"][collector_name] = extra_info_list

        for row in detection_rows:
            det_id = row["id"]
            mapping = sources_by_detection_id.get(det_id, {"sources": [], "extra_info": {}})

            initial_detection_time = {
                "unix": str(row["initial_detection_time_unix"]),
                "text": row["initial_detection_time_text"],
            }

            detections.append(
                {
                    "name": row["name"],
                    "file_hash": row["file_hash"],
                    "sources": mapping["sources"],
                    "initial_detection_time": initial_detection_time,
                    "extra_info": mapping["extra_info"],
                }
            )


def _migrate_json_to_db_if_needed():
    """
    One-time migration from detections/detections.json to SQLite.

    If the database already contains detections or the JSON file does
    not exist, this function is a no-op.
    """
    if not os.path.exists(DETECTIONS_FILE):
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS cnt FROM detections")
            row = cursor.fetchone()
            if row and row["cnt"] > 0:
                # Database already has data; assume migration (or new deployment) has occurred.
                return

            try:
                with open(DETECTIONS_FILE, "r") as detections_file:
                    legacy_detections = json.loads(detections_file.read())
            except Exception as e:
                print(
                    "[!] Could not read legacy detections file {name} for migration!".format(
                        name=DETECTIONS_FILE
                    )
                )
                logging.exception(e)
                return

            for detection in legacy_detections:
                name = detection.get("name")
                file_hash = detection.get("file_hash")
                if not name or not file_hash:
                    continue

                initial = detection.get("initial_detection_time") or {}
                try:
                    initial_unix = int(initial.get("unix", int(time.time())))
                except Exception:
                    initial_unix = int(time.time())
                initial_text = initial.get(
                    "text",
                    time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(initial_unix)),
                )

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO detections
                        (name, file_hash, initial_detection_time_unix, initial_detection_time_text)
                    VALUES (?, ?, ?, ?)
                    """,
                    (name, file_hash, initial_unix, initial_text)
                )
                detection_id = cursor.lastrowid

                # If the row already existed because of INSERT OR IGNORE,
                # fetch its id so we can insert sources correctly.
                if not detection_id:
                    cursor.execute(
                        "SELECT id FROM detections WHERE file_hash = ?",
                        (file_hash,)
                    )
                    existing = cursor.fetchone()
                    if not existing:
                        continue
                    detection_id = existing["id"]

                sources = detection.get("sources", []) or []
                extra_info = detection.get("extra_info", {}) or {}

                for collector_name in sources:
                    extra_list = extra_info.get(collector_name, []) or []
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO detection_sources
                            (detection_id, collector_name, extra_info_json, created_at_unix)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            detection_id,
                            collector_name,
                            json.dumps(extra_list),
                            int(time.time())
                        )
                    )

            conn.commit()
            logging.info(
                "Migrated legacy detections from '{file}' into SQLite.".format(
                    file=DETECTIONS_FILE
                )
            )
    except Exception as e:
        print("[!] Error during migration of detections to SQLite!")
        logging.exception(e)


def load_detections():
    """
    Initialize the SQLite database, perform one-time migration from the
    legacy JSON file if needed, and build the in-memory cache.
    """
    print("[*] Loading detections...")

    init_db()
    _migrate_json_to_db_if_needed()
    _build_cache_from_db()

    logging.info("Loaded detections from SQLite database.")
    return detections


def save_detections():
    """
    No-op for backward compatibility.

    Detections are now stored directly in SQLite, so there is no need
    to explicitly save them on termination.
    """
    print("[*] Detections are stored in SQLite; nothing to save.")


def is_known_hash(file_hash):
    """
    Return True if there is any detection for the given file hash.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM detections WHERE file_hash = ? AND deleted = 0 LIMIT 1",
            (file_hash,)
        )
        return cursor.fetchone() is not None


def is_known_pair(file_hash, collector_name):
    """
    Return True if the given collector has already reported the hash.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1
            FROM detections d
            JOIN detection_sources ds ON d.id = ds.detection_id
            WHERE d.file_hash = ? AND ds.collector_name = ? AND d.deleted = 0
            LIMIT 1
            """,
            (file_hash, collector_name)
        )
        return cursor.fetchone() is not None


def register_detection(name, file_hash, collector_name, extra_info_table):
    """
    Register a detection in SQLite and emit notification.
    """
    extra_info_table = extra_info_table or []

    # Return if this detection is known by this collector
    if is_known_pair(file_hash, collector_name):
        return

    now_unix = int(time.time())
    now_text = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(now_unix))

    with get_connection() as conn:
        cursor = conn.cursor()

        # Does a detection already exist for this hash (including soft-deleted)?
        cursor.execute(
            "SELECT id, initial_detection_time_unix, initial_detection_time_text, name, deleted "
            "FROM detections WHERE file_hash = ?",
            (file_hash,)
        )
        row = cursor.fetchone()

        if row:
            detection_id = row["id"]
            was_deleted = bool(row["deleted"])

            # If the detection was soft-deleted previously, restore it.
            if was_deleted:
                cursor.execute(
                    """
                    UPDATE detections
                    SET deleted = 0,
                        deleted_at_unix = NULL
                    WHERE id = ?
                    """,
                    (detection_id,)
                )

            cursor.execute(
                """
                INSERT OR REPLACE INTO detection_sources
                    (detection_id, collector_name, extra_info_json, created_at_unix)
                VALUES (?, ?, ?, ?)
                """,
                (detection_id, collector_name, json.dumps(extra_info_table), now_unix)
            )

            conn.commit()

            # Keep in-memory cache roughly in sync for compatibility.
            for detection in detections:
                if detection.get("file_hash") == file_hash:
                    if collector_name not in detection["sources"]:
                        detection["sources"].append(collector_name)
                    detection["extra_info"][collector_name] = extra_info_table
                    break

            extra_info_text = ""
            if extra_info_table:
                extra_info_text = "Extra Info:\n\t" + "\n\t".join(extra_info_table)

            if was_deleted:
                # Treat re-detection after soft delete as a fresh detection.
                text = "Detected {name} ({hash}) on {collector}. {extra}".format(
                    name=name,
                    hash=file_hash,
                    collector=collector_name,
                    extra=extra_info_text,
                )
            else:
                text = (
                    "Detected {name} ({hash}) which was previously known, "
                    "on new source {collector}. {extra}"
                ).format(
                    name=name,
                    hash=file_hash,
                    collector=collector_name,
                    extra=extra_info_text,
                )

            broadcast_event(Events.NOTIFY, text)
        else:
            # Else, create a new detection
            initial_detection_time = {
                "unix": str(now_unix),
                "text": now_text,
            }

            cursor.execute(
                """
                INSERT INTO detections
                    (name, file_hash, initial_detection_time_unix, initial_detection_time_text, deleted, deleted_at_unix)
                VALUES (?, ?, ?, ?, 0, NULL)
                """,
                (name, file_hash, now_unix, now_text)
            )
            detection_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO detection_sources
                    (detection_id, collector_name, extra_info_json, created_at_unix)
                VALUES (?, ?, ?, ?)
                """,
                (detection_id, collector_name, json.dumps(extra_info_table), now_unix)
            )

            conn.commit()

            # Update in-memory cache representation.
            extra_info = {collector_name: extra_info_table}
            detection_obj = {
                "name": name,
                "file_hash": file_hash,
                "sources": [collector_name],
                "initial_detection_time": initial_detection_time,
                "extra_info": extra_info
            }
            detections.append(detection_obj)

            extra_info_text = ""
            if extra_info_table:
                extra_info_text = "Extra Info:\n\t" + "\n\t".join(extra_info_table)

            text = "Detected {name} ({hash}) on {collector}. {extra}".format(
                name=name, hash=file_hash, collector=collector_name, extra=extra_info_text
            )
            broadcast_event(Events.NOTIFY, text)


def add_detection_manual(name, file_hash, collector_name="manual", extra_info=None):
    """
    Manually add a detection using the same pipeline as collectors.
    """
    register_detection(name, file_hash, collector_name, extra_info or [])


def remove_detection(file_hash, soft=True):
    """
    Remove a detection by file hash.

    If soft is True, the detection is marked as deleted but kept in the
    database so it can be restored later. If soft is False, the row and
    its associated sources are removed permanently.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        if soft:
            now_unix = int(time.time())
            cursor.execute(
                """
                UPDATE detections
                SET deleted = 1,
                    deleted_at_unix = ?
                WHERE file_hash = ?
                """,
                (now_unix, file_hash)
            )
        else:
            cursor.execute(
                "DELETE FROM detections WHERE file_hash = ?",
                (file_hash,)
            )

        conn.commit()

    # Refresh cache so that CLI or any other consumer sees the change.
    _build_cache_from_db()


def restore_detection(file_hash):
    """
    Restore a soft-deleted detection by file hash.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE detections
            SET deleted = 0,
                deleted_at_unix = NULL
            WHERE file_hash = ?
            """,
            (file_hash,)
        )
        conn.commit()

    _build_cache_from_db()


def remove_detection_source(file_hash, collector_name):
    """
    Remove a specific collector source from a detection.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM detections WHERE file_hash = ?",
            (file_hash,)
        )
        row = cursor.fetchone()
        if not row:
            return

        detection_id = row["id"]
        cursor.execute(
            """
            DELETE FROM detection_sources
            WHERE detection_id = ? AND collector_name = ?
            """,
            (detection_id, collector_name)
        )
        conn.commit()

    # Update cache
    for detection in detections:
        if detection.get("file_hash") == file_hash:
            if collector_name in detection["sources"]:
                detection["sources"].remove(collector_name)
            detection["extra_info"].pop(collector_name, None)
            break


def list_detections(filter_hash=None, filter_collector=None, include_deleted=False):
    """
    Return a list of detections in the same structure as the in-memory cache.
    """
    results = []

    with get_connection() as conn:
        cursor = conn.cursor()

        conditions = []
        params = []

        if not include_deleted:
            conditions.append("d.deleted = 0")

        if filter_hash:
            conditions.append("d.file_hash = ?")
            params.append(filter_hash)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        cursor.execute(
            f"""
            SELECT
                d.id,
                d.name,
                d.file_hash,
                d.initial_detection_time_unix,
                d.initial_detection_time_text,
                d.deleted
            FROM detections d
            {where_clause}
            """,
            tuple(params)
        )
        detection_rows = cursor.fetchall()

        ids = [row["id"] for row in detection_rows]
        if not ids:
            return results

        # Optionally filter by collector name.
        collector_condition = ""
        collector_params = []
        if filter_collector:
            collector_condition = "AND ds.collector_name = ?"
            collector_params.append(filter_collector)

        placeholders = ",".join(["?"] * len(ids))
        cursor.execute(
            f"""
            SELECT
                ds.detection_id,
                ds.collector_name,
                ds.extra_info_json
            FROM detection_sources ds
            WHERE ds.detection_id IN ({placeholders})
            {collector_condition}
            """,
            tuple(ids + collector_params)
        )
        source_rows = cursor.fetchall()

        sources_by_detection_id = {}
        for row in source_rows:
            det_id = row["detection_id"]
            collector_name = row["collector_name"]
            extra_info_json = row["extra_info_json"]
            try:
                extra_info_list = json.loads(extra_info_json) if extra_info_json else []
            except Exception:
                extra_info_list = []

            if det_id not in sources_by_detection_id:
                sources_by_detection_id[det_id] = {
                    "sources": [],
                    "extra_info": {},
                }

            sources_by_detection_id[det_id]["sources"].append(collector_name)
            sources_by_detection_id[det_id]["extra_info"][collector_name] = extra_info_list

        for row in detection_rows:
            det_id = row["id"]
            mapping = sources_by_detection_id.get(det_id, {"sources": [], "extra_info": {}})

            initial_detection_time = {
                "unix": str(row["initial_detection_time_unix"]),
                "text": row["initial_detection_time_text"],
            }

            results.append(
                {
                    "name": row["name"],
                    "file_hash": row["file_hash"],
                    "sources": mapping["sources"],
                    "initial_detection_time": initial_detection_time,
                    "extra_info": mapping["extra_info"],
                    "deleted": bool(row["deleted"]),
                }
            )

    return results


def get_detection(file_hash, include_deleted=False):
    """
    Return a single detection (or None) in the same structure as list_detections.
    """
    detections_list = list_detections(
        filter_hash=file_hash, include_deleted=include_deleted
    )
    return detections_list[0] if detections_list else None


def export_detections_to_file(path, include_deleted=False):
    """
    Export detections to a JSON file for backup or migration purposes.
    """
    data = list_detections(include_deleted=include_deleted)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def import_detections_from_file(path):
    """
    Import detections from a JSON file previously created by export_detections_to_file.
    """
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except Exception as e:
        logging.exception(e)
        return

    for item in data:
        name = item.get("name")
        file_hash = item.get("file_hash")
        sources = item.get("sources", []) or []
        extra_info = item.get("extra_info", {}) or {}

        if not name or not file_hash:
            continue

        for collector_name in sources:
            extra_list = extra_info.get(collector_name, []) or []
            register_detection(name, file_hash, collector_name, extra_list)


subscribe_to_event(Events.INITIALIZE, load_detections)
subscribe_to_event(Events.TERMINATE, save_detections)

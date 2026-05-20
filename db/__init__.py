import os
import sqlite3

DB_FILE_NAME = "fairplay.db"

def _get_db_path():
    """
    Return the absolute path to the SQLite database file.

    The database is placed in the project root directory so that it is
    easy to back up or inspect with external tools.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, DB_FILE_NAME)


def get_connection():
    """
    Return a new SQLite connection.

    Callers are expected to use the connection as a context manager, e.g.:

        with get_connection() as conn:
            ...
    """
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize the SQLite database schema if it does not already exist.

    This function is safe to call multiple times.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Detections represent a unique malicious sample (file_hash) that
        # has been seen at least once.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                initial_detection_time_unix INTEGER NOT NULL,
                initial_detection_time_text TEXT NOT NULL,
                UNIQUE(file_hash)
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_detections_file_hash
                ON detections(file_hash)
            """
        )

        # Soft-delete support: older databases may not have these columns,
        # so we add them conditionally.
        try:
            cursor.execute(
                """
                ALTER TABLE detections
                ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0
                """
            )
        except sqlite3.OperationalError:
            # Column already exists or table is immutable; ignore.
            pass

        try:
            cursor.execute(
                """
                ALTER TABLE detections
                ADD COLUMN deleted_at_unix INTEGER
                """
            )
        except sqlite3.OperationalError:
            # Column already exists or table is immutable; ignore.
            pass

        # Each source entry represents one collector that has detected
        # a particular sample. Extra information from the collector is
        # stored as JSON so that the schema remains flexible.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS detection_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_id INTEGER NOT NULL,
                collector_name TEXT NOT NULL,
                extra_info_json TEXT,
                created_at_unix INTEGER NOT NULL,
                UNIQUE(detection_id, collector_name),
                FOREIGN KEY(detection_id) REFERENCES detections(id)
                    ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_detection_sources_detection_id
                ON detection_sources(detection_id)
            """
        )

        # IOC definitions are still primarily sourced from JSON files
        # in the `ioc` directory, but we mirror them here so that they
        # can be queried and managed more easily.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS iocs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                poll_time INTEGER NOT NULL,
                metadata_json TEXT,
                created_at_unix INTEGER NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                UNIQUE(name)
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_iocs_file_hash
                ON iocs(file_hash)
            """
        )

        conn.commit()


def reset_db() -> dict[str, int]:
    """
    Hard reset: delete all rows from the SQLite tables.

    Returns per-table deleted row counts.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        # Order matters with foreign keys.
        cursor.execute("DELETE FROM detection_sources")
        deleted_sources = cursor.rowcount if cursor.rowcount is not None else 0

        cursor.execute("DELETE FROM detections")
        deleted_detections = cursor.rowcount if cursor.rowcount is not None else 0

        cursor.execute("DELETE FROM iocs")
        deleted_iocs = cursor.rowcount if cursor.rowcount is not None else 0

        conn.commit()

    return {
        "detection_sources": int(deleted_sources),
        "detections": int(deleted_detections),
        "iocs": int(deleted_iocs),
    }


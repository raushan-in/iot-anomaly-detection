"""
Task 1 - Sensor Mapping Data Processing
"""

import csv
import os
import time

from common import get_database_connection, get_s3_client, logger


def fetch_mapping_data():
    """
    Read mapping file from MinIO.

    Returns:
        List[Dict]: A list of rows, each represented as a dictionary.
    """
    s3 = get_s3_client()
    response = s3.get_object(
        Bucket=os.getenv("S3_BUCKET"), Key=os.getenv("MAPPING_PREFIX")
    )
    with response["Body"] as body:
        return list(
            csv.DictReader(body.read().decode("utf-8").splitlines(), delimiter=";")
        )


def ensure_mapping_table_exists(conn):
    """
    Ensure the sensor_mapping table exists in the database.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sensor_mapping (
                sensor_name VARCHAR(50) PRIMARY KEY,
                sensor_uuid UUID UNIQUE NOT NULL
            );
            """
        )
        conn.commit()
    logger.info("Ensured sensor_mapping table exists.")


def insert_mapping_data(conn, mappings):
    """
    Insert mapping data into the database.

    Args:
        conn: Database connection object.
        mappings (List[Dict]): A list of rows to insert into the database.
    """
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO sensor_mapping (sensor_name, sensor_uuid)
            VALUES (%(sensor_name)s, %(sensor_uuid)s)
            ON CONFLICT (sensor_name) DO NOTHING;
            """,
            mappings,
        )
        conn.commit()
    logger.info("Inserted %d rows into sensor_mapping table.", len(mappings))


def transfer_mapping_data():
    """
    Orchestrate the transfer of mapping data from MinIO to PostgreSQL.
    """
    start_time = time.time()
    try:
        logger.info("Fetching mapping data from MinIO...")
        mappings = fetch_mapping_data()

        if not mappings:
            logger.warning("No mapping data found in the source file.")
            return

        logger.info("Connecting to PostgreSQL database...")
        with get_database_connection() as conn:
            ensure_mapping_table_exists(conn)
            insert_mapping_data(conn, mappings)

        logger.info("Data transfer completed successfully!")
    except Exception as e:
        logger.error("An error occurred during data transfer: %s", repr(e))
    finally:
        elapsed_time = time.time() - start_time
        logger.info("Task-1 process completed in %.2f seconds", elapsed_time)


if __name__ == "__main__":
    transfer_mapping_data()

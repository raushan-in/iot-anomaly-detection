"""
Task 2
"""

import csv
import os
import time
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from typing import Dict, List

from common import get_database_connection, get_s3_client, logger

# Number of parallel threads
MAX_WORKERS = int(os.getenv("MAX_THREAD_WORKERS", "8"))


def ensure_sensor_data_table_exists():
    """
    Ensure the sensor_data table exists in the database. \n
    Creates the table if it doesn't already exist.
    """
    with get_database_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sensor_data (
                    timestamp TIMESTAMP NOT NULL,
                    sensor_uuid UUID NOT NULL,
                    sensor_value DOUBLE PRECISION NOT NULL,
                    PRIMARY KEY (timestamp, sensor_uuid)
                );
                """
            )
            conn.commit()
        logger.info("Ensured sensor_data table exists.")


def fetch_file_list_from_minio(prefix: str) -> List[str]:
    """
    Fetch the list of CSV files from MinIO based on the specified prefix.

    Args:
        prefix (str): The directory/prefix in the MinIO bucket.

    Returns:
        List[str]: A list of CSV file keys in the bucket.
    """
    s3 = get_s3_client()
    response = s3.list_objects_v2(Bucket=os.getenv("S3_BUCKET"), Prefix=prefix)
    return [
        obj["Key"]
        for obj in response.get("Contents", [])
        if obj["Key"].endswith(".csv")
    ]


def fetch_file_data_from_minio(key: str) -> List[Dict[str, str]]:
    """
    Fetch and parse an entire CSV file from MinIO into a list of dictionaries.

    Args:
        key (str): The S3 key (file path) of the CSV file.

    Returns:
        List[Dict[str, str]]: A list of rows, each represented as a dictionary.
    """
    s3 = get_s3_client()
    response = s3.get_object(Bucket=os.getenv("S3_BUCKET"), Key=key)
    with StringIO(response["Body"].read().decode("utf-8")) as f:
        return list(csv.DictReader(f, delimiter=";"))


def bulk_insert_sensor_data(data: List[Dict[str, str]]):
    """
    Insert sensor data into the database using the PostgreSQL COPY command.

    Args:
        data (List[Dict[str, str]]): The sensor data to insert.
    """
    with get_database_connection() as conn:
        with conn.cursor() as cur:
            # Write data into a temporary buffer for bulk COPY
            buffer = StringIO()
            for row in data:
                buffer.write(
                    f"{row['timestamp']}\t{row['sensor_uuid']}\t{row['sensor_value']}\n"
                )
            buffer.seek(0)
            cur.copy_expert(
                """
                COPY sensor_data (timestamp, sensor_uuid, sensor_value)
                FROM STDIN WITH (FORMAT CSV, DELIMITER '\t');
                """,
                buffer,
            )
            conn.commit()
    logger.info("Inserted %d rows into sensor_data table.", len(data))


def process_file(file_key: str):
    """
    Process a single CSV file from MinIO.

    Args:
        file_key (str): The S3 key of the file to process.
    """
    try:
        logger.info("Processing file: %s", file_key)
        data = fetch_file_data_from_minio(file_key)
        bulk_insert_sensor_data(data)
        logger.info("Successfully processed file: %s", file_key)
    except Exception as e:
        logger.error("Failed to process %s: %s", file_key, repr(e))


def transfer_sensor_data():
    """
    Orchestrate the transfer of sensor data from MinIO to PostgreSQL.
    """
    start_time = time.time()
    try:
        ensure_sensor_data_table_exists()

        # Fetch the list of files from MinIO
        prefixes = os.getenv("DATA_PREFIXES").split(",")
        all_files = []
        for prefix in prefixes:
            all_files.extend(fetch_file_list_from_minio(prefix))
        logger.info("Found %d CSV files.", len(all_files))

        # Process files concurrently
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(process_file, all_files)

        logger.info("Sensor data transfer completed successfully!")
    except Exception as e:
        logger.error("An error occurred: %s", e)
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info("Task-2 process completed in %.2f seconds", elapsed_time)


if __name__ == "__main__":
    transfer_sensor_data()

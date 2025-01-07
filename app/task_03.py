"""
Task 3
"""

import argparse

import pandas as pd
from common import get_database_connection, logger


def fetch_sensor_data(
    sensor_name: str, start_timestamp: str, end_timestamp: str
) -> pd.DataFrame:
    """
    Fetches measurements for a specific sensor within a given time range.

    Args:
        sensor_name (str): The name of the sensor.
        start_timestamp (str): The start of the time range (YYYY-MM-DD HH:MM:SS format).
        end_timestamp (str): The end of the time range (YYYY-MM-DD HH:MM:SS format).

    Returns:
        pd.DataFrame: A DataFrame containing the sensor measurements within the specified time range.
    """
    try:
        logger.info(
            "Fetching sensor data for sensor: %s, Time range: %s to %s",
            sensor_name,
            start_timestamp,
            end_timestamp,
        )

        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                # join `sensor_mapping` and `sensor_data` tables
                query = """
                SELECT m.sensor_name, d.timestamp, d.sensor_value
                FROM sensor_data d
                JOIN sensor_mapping m ON d.sensor_uuid = m.sensor_uuid
                WHERE m.sensor_name = %s
                  AND d.timestamp BETWEEN %s AND %s
                ORDER BY d.timestamp;
                """
                cursor.execute(query, (sensor_name, start_timestamp, end_timestamp))

                # Fetch data into a pandas DataFrame
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=columns)

                logger.info(
                    "Successfully fetched %d rows for sensor: %s", len(df), sensor_name
                )
                return df

    except Exception as e:
        logger.error("Error fetching sensor data: %s", repr(e))
        return pd.DataFrame()


def main(sensor_name: str, start_timestamp: str, end_timestamp: str):
    """
    Main function to fetch and output sensor data.

    Args:
        sensor_name (str): The name of the sensor.
        start_timestamp (str): The start of the time range (YYYY-MM-DD HH:MM:SS format).
        end_timestamp (str): The end of the time range (YYYY-MM-DD HH:MM:SS format).
    """
    logger.info("Starting Task 03...")
    result = fetch_sensor_data(sensor_name, start_timestamp, end_timestamp)

    if result.empty:
        logger.info(
            "No data found for sensor: %s within the time range: %s to %s",
            sensor_name,
            start_timestamp,
            end_timestamp,
        )
    else:
        logger.info(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch sensor data for a given time range."
    )
    parser.add_argument("sensor_name", type=str, help="Name of the sensor")
    parser.add_argument(
        "start_timestamp",
        type=str,
        help="Start of the time range (YYYY-MM-DD HH:MM:SS format)",
    )
    parser.add_argument(
        "end_timestamp",
        type=str,
        help="End of the time range (YYYY-MM-DD HH:MM:SS format)",
    )

    args = parser.parse_args()
    main(args.sensor_name, args.start_timestamp, args.end_timestamp)

import argparse

import numpy as np
import pandas as pd
import ruptures as rpt
from common import get_database_connection, logger
from sklearn.linear_model import LinearRegression


def fetch_sensor_data(sensor_name: str):
    """
    Fetch all sensor data for a given sensor name from the database.
    """
    with get_database_connection() as conn:
        query = """
        SELECT timestamp, sensor_value
        FROM sensor_data
        WHERE sensor_uuid = (
            SELECT sensor_uuid FROM sensor_mapping WHERE sensor_name = %s
        )
        ORDER BY timestamp;
        """
        data = pd.read_sql(query, conn, params=(sensor_name,))
    return data


def detect_change_points(data: pd.Series, model="l2"):
    """
    Detect change points in the time series data using Ruptures. \n
    Change points are locations in the time series where the statistical properties
    of the data, such as mean, change significantly
    """
    pen = max(10, len(data) * 0.01)  # Dynamic penalty based on data length
    algo = rpt.Pelt(model=model).fit(data.values)
    return algo.predict(pen=pen)


def fit_piecewise_regression(data: pd.DataFrame, change_points: list):
    """
    piecewise regression models to the segmented data. \n
    Calculates the residuals, which are the differences between the actual sensor values (sensor_value)
    and the predicted values (fitted). \n
    Residuals help identify deviations from the model, which may indicate anomalies or noise.
    """
    data["fitted"] = np.nan
    for i in range(len(change_points) - 1):
        start, end = change_points[i], change_points[i + 1]
        segment = data.iloc[start:end]
        X = np.arange(len(segment)).reshape(-1, 1)
        y = segment["sensor_value"].values.reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, y)

        # The model predicts y (sensor values) based on the index (X) in the segment.
        predicted = model.predict(X)
        data.loc[segment.index, "fitted"] = predicted.flatten()
    data["residual"] = data["sensor_value"] - data["fitted"]
    return data


def detect_anomalies(data: pd.DataFrame, threshold: float = 3.0):
    """
    Detect anomalies based on residuals.
    """
    std_deviation = np.std(data["residual"].dropna())
    data["is_anomaly"] = np.abs(data["residual"]) > (threshold * std_deviation)

    logger.info(
        f"Standard Deviation: {std_deviation}, Deviation Threshold: {threshold}"
    )
    return data[data["is_anomaly"]]


def process_sensor(sensor_name):
    """
    Process data for a sensor: detect change points, fit piecewise regression,
    and identify anomalies.
    """
    logger.info(f"Processing sensor: {sensor_name}")
    try:
        # Fetch all data for the sensor
        data = fetch_sensor_data(sensor_name)
        logger.info(f"Fetched {len(data)} rows for sensor: {sensor_name}")

        # Detect change points
        change_points = detect_change_points(data["sensor_value"])

        # Calculate `residuals` by piecewise regression
        data = fit_piecewise_regression(data, [0] + change_points)

        # Detect anomalies
        anomalies = detect_anomalies(data)

        # Log if any anomalies are found
        if not anomalies.empty:
            logger.info(
                f"Anomaly detected in {sensor_name}: {len(anomalies)} anomalies found."
            )
            logger.info(anomalies)
        else:
            logger.info(f"No anomaly detected in {sensor_name}.")

    except Exception as e:
        logger.error(f"Error processing sensor {sensor_name}: {e}")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            description="Anomalies detection a given sensor."
        )
        parser.add_argument("sensor_name", type=str, help="Name of the sensor")
        args = parser.parse_args()
        process_sensor(args.sensor_name)

    except Exception as e:
        logger.error(f"Error in main execution: {e}")

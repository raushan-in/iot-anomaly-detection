### General Notes

## **Overview**
This project is built with **Python 3.11** for its performance improvements and compatibility with modern libraries. It uses **Docker** for containerization, ensuring consistent environments across different systems.

---

## **Setup Instructions**
1. **Environment Variables**:
   - Create a `.env` file using `example.env` as a reference.
   - Replace placeholders with actual credentials.

2. **Build and Run**:
   - Build and start the container:
     ```bash
     docker compose up --build -d
     ```

3. **Dependencies**:
   - All dependencies are listed in `requirements.txt` and are installed automatically during container build.

---

## **Project Structure**

- All task files are inside the `app` folder.
- The notebook (`task_04_analysis.ipynb`) demonstrates the thought process and anomaly detection methodology.

```
app/
├── __init__.py             # Empty file to make app a module
├── common.py               # Shared utilities (logging, DB connection)
├── task_01.py              # Sensor mapping ingestion
├── task_02.py              # Time-series sensor data ingestion
├── task_03.py              # Query sensor data
├── task_04.py              # Anomaly detection
├── task_04_analysis.ipynb  # Notebook for analyzing sensor data and anomaly

```

---

### Notes for Task 1

1. **Choice of Database (PostgreSQL)**:  
   PostgreSQL was chosen for its reliability, scalability, and ability to efficiently handle large, simple relational datasets.

2. **Choice of Data Model/Schema**:  
   The schema ensures data integrity through a primary key (`sensor_name`) and a unique constraint (`sensor_uuid`) in the `sensor_mapping` table, supporting efficient lookups and preventing duplicates. It is designed to maintain a clear and optimized relationship between sensors and their data.

2. **Command to run task-1 script**:  
-  `docker exec -it iot-app python task_01.py`

---

### Notes for Task 2

This solution ensures scalability by processing data incrementally at the file level. Multiple files are fetched concurrently from MinIO using a `ThreadPoolExecutor`, where the number of threads is configurable to balance performance and resource utilization. PostgreSQL's `COPY` command is utilized for bulk insertion, optimizing data ingestion for large datasets. This design allows efficient handling of large-scale data while maintaining a balance between scalability, memory usage, and processing speed.

### **Required Notes for Task 2**

1. **Choice of Database (TimescaleDB-enabled PostgreSQL)**:
   TimescaleDB was chosen as the database because it offers a strong balance between performance, scalability, and SQL capabilities, making it ideal for large-scale IoT sensor time-series data requiring both historical analysis and integration with relational metadata.
   It has features like hypertables, which optimize queries for large datasets by partitioning data into manageable chunks, provides better performance and scalability for analytical workloads.


2. **Comparison**:
   - **TimescaleDB vs. InfluxDB**: InfluxDB is another popular choice for time-series data. However, TimescaleDB offers SQL compatibility, making it easier to integrate into existing PostgreSQL-based systems and use with SQL-based analytics tools.
 

3. **Choice of Data Schema**:
   - A primary key (`timestamp, sensor_uuid`) ensures uniqueness and fast lookups.
   - Structured schema leverages indexing for efficient querying, enabling rapid processing of millions of records.

4. **Command to run task-2 script**:
- `docker exec -it iot-app python task_02.py`

---


### Notes for Task 3

1. **Performance at Larger Scales**:
The current implementation efficiently handles the existing dataset (~4.5 GB) due to well-designed indexing and schema. However, as the data scales by 10x (~45 GB), 100x (~450 GB), or 1000x (~4.5 TB), fetching entire query results into memory may lead to significant memory bottlenecks and slower performance. To handle such scales, implementing incremental data fetching using pagination or chunking would be essential.

The schema is well-designed for the current use case. Indexes on timestamp and sensor_uuid in the sensor_data table, along with the unique constraint on sensor_uuid in the sensor_mapping table, ensure efficient time-based queries on current dataset.
However, as the data grows, the efficiency of these indexes may diminish due to the increasing number of rows. To sustain performance at larger scales, strategies like partitioning (e.g., by time ranges in sensor_data) or leveraging TimescaleDB specific optimizations like hypertables may be required. These techniques would ensure that query execution remains efficient even with exponential data growth.

2. **Command to run task-3 script**: (multiple examples)
- `docker exec -it iot-app python task_03.py "sensor_00354" "2012-12-31 23:53:00+01:00" "2013-01-01 00:43:00+01:00"`
- `docker exec -it iot-app python task_03.py "sensor_00010" "2012-12-31 23:53:00+01:00" "2013-10-10 00:43:00+01:00"`
- `docker exec -it iot-app python task_03.py "sensor_00000" "2023-12-31 23:53:00+01:00" "2023-01-10 00:43:00+01:00"`

---

### Notes for Task 4

1. **Plotting the data in advance**:
The data was plotted to explore time-series relationships and trends. This allowed me to identify patterns, outliers, and abrupt changes in sensor values, which helped me in the approach for further analysis and anomaly detection. Ref: app/`task_04_analysis.ipynb`

2. **Fitting a regression model and strategy for piecewise regression**:

Regression model was used to capture the relationship between timestamps and sensor values. Piecewise regression was applied using change point detection to segment the time series into distinct regions, fitting separate models for each segment to better capture variations. Used `ruptures' for data segmentation. 

3. **Reasoning for the existence of anomalies**:

Anomalies were found based on significant deviations from expected behavior. Residuals (differences between observed and predicted values) were analyzed. Observations with residuals beyond 3 standard deviations from the mean indicated potential anomalies.

4. **Strategy for detecting anomalies:**:

The strategy involved detecting change points to segment the data, applying regression models to fit each segment, and calculating residuals. A threshold of 3 standard deviations was used to identify anomalies where residuals exceeded the threshold. This automated process ensures effective anomaly detection.
Based on sensor specific behavior and use cases, there is a scope of improvements by adjusting the detectiion threshold (Based on observation over very limited data and scenario, currently set as 3).

5. **Command to run task-4 script**: (with a example)
- `docker exec -it iot-app python task_04.py sensor_00317`
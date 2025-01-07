# About
This document contains all the information for the data engineering challenge.

It is split into the following sections. You must read all the sections if you are to be able to solve the task.

1. **Data**: This section contains the description of the data files provided. It explains the data format in the context of a fictitious but realistic IOT company scenario.
2. **Tasks**: This section describes the tasks you need to perform. You will be judged based on your performance on these tasks. Each task also has some sub-tasks and additional information. Please read the task descriptions clearly before attempting to work on the task.
3. **Guidelines**: These are guidelines we expect you to follow when solving the tasks.

# Data
There is a fictitious IOT company that has deployed a lot of sensors in a building. Each sensor monitors temperature and other ambient variables and generates a single floating point value that encodes all the measurements at a given point in time. The sensor sends this single floating point value to a backend server every few minutes. These values or measurements are collected in CSV files.

Every sensor has two identities (IDs). One is called its `sensor_name` which is a humanreadable name. An example of `sensor_name` is `sensor_00000`. The engineers at the company refer to a sensor by its `sensor_name`. The other identity of the sensor is called its `sensor_uuid`. An example of `sensor_uuid` is `efa4b573-e1b1-46b3-9e8a-0b303d2bb66e`. The backend server refers to a sensor by its `sensor_uuid`.    

There are two kinds of CSV files. One is called Mapping CSV and the other is called a Data CSV.

The Mapping CSV contains a one-to-one mapping between `sensor_name` and `sensor_uuid`. An engineer uses the Mapping CSV to find the corresponding `sensor_uuid` for the `sensor_name` that they are interested in. There is only one Mapping CSV file, and it is called `mapping.csv`. Here is an example of what the Mapping CSV looks like:
```text
sensor_name;sensor_uuid
sensor_00000;efa4b573-e1b1-46b3-9e8a-0b303d2bb66e
sensor_00001;b1a99a56-0e47-4f4d-9e07-963d3e228eca
sensor_00002;5e24cdb4-3608-4f01-bc90-822dbcf9ebad
```

The Data CSV contains all the measurements taken by all the sensors. Every measurement taken by the sensor consists of three parts. The first is the `timestamp` of when the measurement was taken. The second is the `sensor_uuid` of the sensor. The last is the `sensor_value` which is the floating point reading of the sensor. The measurements of all the sensors found in `mapping.csv` can be found in `data.csv`. You might find some data csvs have more columns but Here is an example of columns in Data CSV that we are intersted in:
```text
timestamp;sensor_uuid;sensor_value
2015-12-31 23:53:00;59b4fd2b-b3c7-43c0-bffc-f661b6aeaacf;-75.33380361808872
2015-12-31 23:53:00;34f19991-8632-482d-9693-b106a8691e8b;2052.0067766516345
2015-12-31 23:53:00;68991bb4-e31c-4452-8ca7-55673a1f8d41;-380.22246350898695

```

# Tasks

An engineer at the company would like to analyse the sensor measurements and find anomalies. They would like to be able to have access to the sensor data by providing the following details:
* The `sensor_name` that identifies the sensor.
* The start and end `timestamps` which indicates the time range of the sensor meansurements they are interested in.

***Note: Mapping and Timeseries data can be found [here](http://164.90.237.89:9001/login) in a object store bucket `code-challenge-data`, access creds have been already sent via email to you! To access the data via s3 API use port `9000` in your config! *** 

It is the job of the Data Engineer to meet the data needs of engineer and analyst. In order to do so, they have to complete the following fours tasks.

1. Write a python script to transfer data from the `mapping.csv` on object-store to a database.
    * You can use any database of your choice. You could use the databases provided in the docker-compose.yml file or something else. You can share the database across all tasks.
    * Required notes: What are your motivations for your choice of database i.e. why did you choose the database that you chose?
    * Required notes: What are your motivations for your choice of data model or database schema?
    * Required notes: Provide instructions on running the script? (E.g. `$ python task_01.py`)
2. Write a python script to transfer the Data CSVs for all sensors from the `Timeseries` directory including sub directories on the objec-store to a database.
    * Please use all csv files that are in `Timeseries` directory including sub directories.
    * You need to use a different database than the one you chose for Task 1. Different databases have different strengths. You can use any database of your choice (except for the one from task 1). 
    * You can share the database across all tasks.
    * You can assume that all the data given is located in the timezone `Europe/Berlin` but some csv timestamps are not timezone aware.
    * Required notes: What are your motivations for your choice of database i.e. why did you choose the database that you chose? 
    * Required notes: What are your motivations for your choice of data model or database schema?
    * Required notes: Provide instructions on running the script? (E.g. `$ python task_02.py`)
3. Write a python script or python function that accepts `sensor_name`, `start_timestamp` and `end_timestamp` as arguments and outputs the measurements for that sensor and time range.
    * We expect that you will query for the data from the database or databases that you have in Task 1 and Task 2.
    * The output of the python script or function may be any Python object (data type) of your choice (E.g. List, Set, pandas.DataFrame, etc)
    * Required notes: How will your code perform when the amount of data scales by 10x, 100x or 1000x? Your code is not expected to handle that scale of data. We only want to know if you understand the performance characteristics of the code you've written.
    * Required notes: Provide instructions on running the script? (E.g. `$ python task_03.py`)
4. Analyze the sensor data for all sensors that have data in `data_*.csv`s and write down your strategy for programatically finding anomalies in sensor data if they exist.
    * You might want to plot the data in advance to see which kind of relations we are searching for.
    * We expect that you will fit a suitable regression model for the sensor data. For some sensors, you might think of a strategy where you need to fit piecewise regressions.
    * Required notes: Provide your reasoning for why you think there exist anomalies or why you think there don't exist any anomalies.
    * Required notes: If you think the data consists of anomalies, please mention a programmatic/mathematical strategy to find these anomalies automatically.
    

# Guidelines
* All code and information provided in this repository is confidential and cannot be shared with any third party.
* These are the steps we would like you to follow in solving this challenge:
    1. We expect that you have already made GitHub accounts and that we would have already added you as collaborators to this repository.
    1. Commit and push your solution to the repository.
    1. We recommend you keep it simple and not have more than one or two branches.
    1. Once you are done with your solution and have added notes to your `SOLUTION.md` file, then write us an email that you are finished.
    1. We will then have a look at your work (and if required clone it locally to run your code) to judge your performance.
* When solving the programming tasks, please stick to the task requirements. You are not expected to do anything beyond the scope of the tasks.
    * In case you have questions, do not hesitate to ask or clarify from us, especially if it is something that might help you simplify your code or thought process.
    * Task 1 and Task 2 are closely related to each other. If you would like to solve both Task 1 and Task 2 together under one roof, please feel free to do so. You can merge Task 2 into Task 1 i.e. you can write all your code and notes for Task 1 and leave Task 2 empty.
    * Task 1 and Task 2 are about storing the data in a database. The term `database` is defined loosely. You can choose any disk based database or filesystem strategies to solve the tasks.
* Please provide the notes for the tasks. Your notes and comments that we expect are described under the `Required notes: ...` bullet points. Please write your notes in the SOLUTIONS.md file under the right header. We only expect one, two or three bullet points for each of the `Required notes` at the most.
* Please write clean and well documented code.
    * You may use sensible hard-coded values within your python scripts such as database URIs, paths to CSV files etc.
    * You are free to use type hints.
* Python version and depedencies:
    * Please mention which version of python your code is written for. We expect the python version to be at least `>=3.9`.
    * Please add all of your dependencies to the `requirements.txt` file. If we have to run your code, we will first run the following command `pip install -r requirements.txt`
* Project structure:
    * You are free to reorganize the files and folders as you wish. We recommend you stick to a simple folder structure and write your code within task specific files.
    * You may add additional python files if it helps you organize your code better.
* Finally, please do not over-engineer your solutions. Above all, we are looking for simplicity and elegance in your solutions. A simple solution that works as expected is the first solution that gets pushed to production and adds value.


# References

1. Incase you would like to use Docker and the `docker-compose.yml` file that is provided.
    * [Official Docker Installation Guide](https://docs.docker.com/engine/install/)
    * [Docker Installation Guide for Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)
    * Here are some`docker-compose` commands to quickly start you off. The following commands must be run at the root of the repository i.e. the same directory where the `docker-compose.yml` file is located. 
      ```text
      # Install docker-compose
      $ pip install docker-compose
      
      # To start postgres & scylla containers, in a new terminal window run the following command
      $ docker-compose up
      
      # To access to psql on the Postgres container, in a new terminal window run the following command
      $ docker exec -it rg-postgres-c psql -U postgres
      
      # To access to cqlsh on the ScyllaDB container, in a new terminal window run the following command
      $ docker exec -it rg-scylla-c cqlsh
      
      # To kill the containers and remove all data from containers
      $ docker-compose down -v
      ```
      
    
# iot-anomaly-detection

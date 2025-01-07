"""
Common Operations
"""

import logging
import os
from contextlib import contextmanager

import boto3
from botocore.config import Config
from dotenv import load_dotenv
from psycopg2 import pool

# Load environment variables from .env
load_dotenv()

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

db_pool = None


def initialize_db_pool():
    """Initialize and return a PostgreSQL connection pool."""
    global db_pool
    if not db_pool:
        db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
        )
        if not db_pool:
            raise ConnectionError("Failed to initialize the database connection pool.")
        logger.info("Database connection pool initialized.")


@contextmanager
def get_database_connection():
    """
    Context manager for database connection.

    Automatically initializes the connection pool if it hasn't been initialized yet.
    Ensures that connections are returned to the pool after use.
    """
    global db_pool
    if not db_pool:
        initialize_db_pool()

    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)


def get_s3_client():
    """Return a configured Boto3 S3 client."""
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
        config=Config(retries={"max_attempts": 3, "mode": "standard"}),
    )

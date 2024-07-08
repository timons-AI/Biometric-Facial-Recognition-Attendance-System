import mysql.connector
from mysql.connector import Error, pooling
import logging
from config import Config
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None
        self.create_pool()

    def create_pool(self):
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=5,
                pool_reset_session=True,
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB
            )
            logger.info("Connection pool created successfully")
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")

    def get_connection(self):
        retries = 3
        while retries > 0:
            try:
                connection = self.pool.get_connection()
                return connection
            except Error as e:
                logger.error(f"Error getting connection from pool: {e}")
                retries -= 1
                time.sleep(1)
        raise Exception("Failed to get database connection after multiple attempts")

    def execute_query(self, query, params=None):
        with self.get_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                connection.commit()
                return cursor
            except Error as e:
                connection.rollback()
                logger.error(f"Error executing query: {e}")
                raise

    def fetch_all(self, query, params=None):
        with self.get_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    return cursor.fetchall()
            except Error as e:
                logger.error(f"Error fetching data: {e}")
                raise

    def fetch_one(self, query, params=None):
        with self.get_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    return cursor.fetchone()
            except Error as e:
                logger.error(f"Error fetching data: {e}")
                raise

    def close(self):
        if self.pool:
            self.pool.close()
            logger.info("Connection pool closed")
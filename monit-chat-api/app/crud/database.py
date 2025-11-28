import os
import pymongo
import psycopg2
import psycopg2.extensions
from datetime import datetime, date

from app.crud.exceptions import QueryCannotBeExecuted

MONGO_APP_DB = os.getenv("MONGO_APP_DB", "appdb")

class MongoConnection:
    _client = None

    @classmethod
    def get_client(cls):
        """
        Mongo singleton connection creation
        """
        mongo_app_db = os.getenv("MONGO_APP_DB", "appdb")
        
        if cls._client is None:
            mongo_port = os.getenv("MONGO_PORT", "27018")
            mongo_host = os.getenv("MONGO_HOST", "mongodb")
            mongo_app_user = os.getenv("MONGO_APP_USER", "appuser")
            mongo_app_pass = os.getenv("MONGO_APP_PASS", "password")

            mongo_uri = f"mongodb://{mongo_app_user}:{mongo_app_pass}@{mongo_host}:{mongo_port}/{mongo_app_db}?authSource={mongo_app_db}"
            cls._client = pymongo.MongoClient(mongo_uri)
        
        return cls._client[mongo_app_db]

class PostgresConnection:
    _connection = None

    @classmethod
    def get_connection(cls):
        """
        PostgreSQL singleton connection creation
        """
        postgres_dw_db = os.getenv("DW_DB_NAME", "appdb")

        if cls._connection is None:
            postgres_host = os.getenv("DW_DB_HOST", "postgres")
            postgres_port = os.getenv("DW_DB_PORT", "5432")
            postgres_user = os.getenv("DW_DB_USER", "appuser")
            postgres_pass = os.getenv("DW_DB_PASSWORD", "password")

            cls._connection = psycopg2.connect(
                host=postgres_host,
                port=postgres_port,
                dbname=postgres_dw_db,
                user=postgres_user,
                password=postgres_pass
            )

        cls.configure_connection_cast_date_to_datetime()
        return cls._connection
    
    def configure_connection_cast_date_to_datetime():
        DATE_as_datetime = psycopg2.extensions.new_type(
            (1082 ,), 
            "DATE",
            lambda value, cursor: None if not value else datetime.fromisoformat(value)
        )
        psycopg2.extensions.register_type(DATE_as_datetime)

        # DECIMAL/NUMERIC → float
        DECIMAL_as_float = psycopg2.extensions.new_type(
            (1700,),  # NUMERIC OID
            "NUMERIC",
            lambda value, cursor: None if not value else float(value)
        )
        psycopg2.extensions.register_type(DECIMAL_as_float)

    def execute_query(self, query, params=None):
        """
        Executes a SQL query and returns the result as a list of dicts.
        Commits automatically for write operations.
        """
        conn = self.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                
                # Se for SELECT, retorna resultado
                if cursor.description:
                    result = cursor.fetchall()
                    columns = [ column.name for column in cursor.description ]
                    return columns, result         
                return None, None
        except Exception as e:
            print(str(e))
            conn.rollback()
            return None, None

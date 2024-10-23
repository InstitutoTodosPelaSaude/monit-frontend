import os
import sys
import subprocess
from minio import Minio
from minio.error import S3Error

def check_minio():
    """
    Test connection to MinIO storage.
    """

    # Get environment variables
    endpoint   = os.getenv("MINIO_ENDPOINT")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")

    if not endpoint or not access_key or not secret_key:
        return False, "Missing one or more required MinIO environment variables (MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY). Check the .env file."

    try:
        # Initialize MinIO client
        minio_client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        # Perform a basic check, e.g., list buckets
        minio_client.list_buckets()
        return True, "MinIO connection successful."
    except S3Error as err:
        return False, f"MinIO connection failed: {err}"


def check_database_variables():

    # Define the database variable names for each database
    databases = {
        "Arbo": {
            "HOST": "DB_ARBO_HOST",
            "PORT": "DB_ARBO_PORT",
            "USER": "DB_ARBO_USER",
            "PASSWORD": "DB_ARBO_PASSWORD",
            "DATABASE": "DB_ARBO_DATABASE"
        },
        "Respat": {
            "HOST": "DB_RESPAT_HOST",
            "PORT": "DB_RESPAT_PORT",
            "USER": "DB_RESPAT_USER",
            "PASSWORD": "DB_RESPAT_PASSWORD",
            "DATABASE": "DB_RESPAT_DATABASE"
        },
        "Dagster Arbo": {
            "HOST": "DB_DAGSTER_ARBO_HOST",
            "PORT": "DB_DAGSTER_ARBO_PORT",
            "USER": "DB_DAGSTER_ARBO_USER",
            "PASSWORD": "DB_DAGSTER_ARBO_PASSWORD",
            "DATABASE": "DB_DAGSTER_ARBO_DATABASE"
        },
        "Dagster Respat": {
            "HOST": "DB_DAGSTER_RESPAT_HOST",
            "PORT": "DB_DAGSTER_RESPAT_PORT",
            "USER": "DB_DAGSTER_RESPAT_USER",
            "PASSWORD": "DB_DAGSTER_RESPAT_PASSWORD",
            "DATABASE": "DB_DAGSTER_RESPAT_DATABASE"
        }
    }
    
    missing_vars = []

    # Check each database's variables
    for database, variables in databases.items():
        for variable_name, env_var in variables.items():
            if not os.getenv(env_var):
                missing_vars.append(f"{env_var} for {database}")

    if missing_vars:
        return False, f"Missing environment variables: {', '.join(missing_vars)}."
    
    return True, "All required database environment variables are set."

def healthcheck():
    # Run multiple health checks
    checks = {
        "MinIO Check": check_minio,
        "Database .env variables Check": check_database_variables
    }

    all_healthy = True
    for name, check in checks.items():
        healthy, message = check()
        if not healthy:
            print(f"{name} FAILED: {message}")
            all_healthy = False
        else:
            print(f"{name}: {message}")

    if all_healthy:
        sys.exit(0)  # Healthy
    else:
        sys.exit(1)  # Unhealthy

if __name__ == "__main__":
    healthcheck()

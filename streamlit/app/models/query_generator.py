
import requests

QUERY_API_URL = "http://query:8000"

def fetch_sql_query(question, project, table="combined", configs={}):
    try:
        response = requests.post(
            f"{QUERY_API_URL}/query",
            json={"question": question, "project": project, "table": table, "configs":configs },
        )
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("sql", "No query found"), response_data.get("raw_sql", "No query found")
    except requests.exceptions.RequestException as e:
        return None
    
def format_sql_query(sql_raw_query, configs={}):
    try:
        response = requests.post(
            f"{QUERY_API_URL}/process",
            json={"sql_raw_query": sql_raw_query, "configs":configs },
        )
        response.raise_for_status()
        
        response_data = response.json()
        return response_data.get("sql", "No query found"), response_data.get("raw_sql", "No query found")
    except requests.exceptions.RequestException as e:
        return None
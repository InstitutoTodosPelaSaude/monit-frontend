import streamlit as st
import sqlparse

import os
import json
from openai import OpenAI

import duckdb

import streamlit as st
import requests

@st.cache_resource()
def get_connection():
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    
    conn = duckdb.connect(database=':memory:', read_only=False)
    conn.execute(f"""
        INSTALL httpfs;
        LOAD httpfs;
        SET s3_region='us-east-1'; -- This is ignore by MinIO
        SET s3_url_style='path';
        SET s3_endpoint='{MINIO_ENDPOINT}';
        SET s3_access_key_id='{MINIO_ACCESS_KEY}';
        SET s3_secret_access_key='{MINIO_SECRET_KEY}';
        SET s3_use_ssl = false;
    """)
    return conn

def query_database(sql_query):

    conn = get_connection()

    df = conn.execute(sql_query).fetchdf()

    return df

def fetch_sql_query(question, project):

    try:
        print({"question": question, "project": project, "table": "combined"},)
        response = requests.post(
            "http://query:8000/query",
            json={"question": question, "project": project, "table": "combined"},
        )
        response.raise_for_status()
        
        response_data = response.json()
        return response_data.get("sql", "No query found"), response_data.get("raw_sql", "No query found")
    except requests.exceptions.RequestException as e:
        return None

def widget_query( container ):

    # Project selection
    project, table = widget_select_project_table(st.sidebar)

    container.markdown(f"Ask me anything about table **{table}** of **{project}**")

    # Question input
    col_question, col_button_go = container.columns( [ 4, 1 ] )
    question = col_question.text_input("", label_visibility = 'collapsed')

    # SQL query prompt processing
    sql_query = None

    if not col_button_go.button("Go!"):
        return

    if not question.strip():
        col_question.warning("Please enter a valid question.")

    try:
        sql_query, sql_raw_query = fetch_sql_query(question, project)
    except Exception as e:
        container.error(f"An error occurred: {e}")
        return

    if not sql_query:
        return

    try:
        data = query_database(sql_query)
    except Exception as e:
        container.error(f"An error occurred: {e}")
        return

    container.divider()
    container.markdown("### Results")
    container.dataframe(data)

    sql_query_formatted = sqlparse.format(sql_raw_query, reindent=True, keyword_case='upper')

    toggle_code = container.expander("Query", False)        
    toggle_code.code(sql_query_formatted, language="sql")

def widget_select_project_table(container):
    
    project_tables = {
        "ARBO":["COMBINED"],
        "RESPAT":["COMBINED"]
    }

    container.title("Tables")

    project = container.selectbox(
        "Project", 
        ["ARBO", "RESPAT"], 
        label_visibility = 'collapsed',
        key = "project_table"
    )

    table = container.radio(
        "**Arboviroses**",
        options=project_tables[project],
        key=f"tables_{project}"
    )

    return project, table

if __name__ == "__main__":
    # Streamlit UI
    st.title("🤖 Monit Chat :dna:")
    sidebar = st.sidebar

    widget_query(st)

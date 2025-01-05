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

def fetch_sql_query(question, project, table="combined", configs={}):

    try:
        response = requests.post(
            "http://query:8000/query",
            json={"question": question, "project": project, "table": table, "configs":configs },
        )
        response.raise_for_status()
        
        response_data = response.json()
        return response_data.get("sql", "No query found"), response_data.get("raw_sql", "No query found")
    except requests.exceptions.RequestException as e:
        return None

def widget_query(container):

    # Project selection and Query Configuration
    project, table = widget_select_project_table(st.sidebar)
    st.sidebar.divider()
    configs = widget_configs(st.sidebar)

    container.markdown(f"Ask me anything about table **{table}** of **{project}**")

    # Question input
    col_question, _ = container.columns( [ 4, 1 ] )

    question = col_question.text_input("", label_visibility = 'collapsed')


    # Check if a question was inputed
    if not question.strip():
        return

    sql_query = None
    try:
        sql_query, sql_raw_query = fetch_sql_query(question, project, configs=configs)
    except Exception as e:
        container.error(f"An error occurred: {e}")
        return

    if not sql_query:
        return

    container.divider()
    container.markdown("### Results")

    sql_query_formatted = sqlparse.format(sql_raw_query, reindent=True, keyword_case='upper')

    toggle_code = container.expander("Query", False)        
    toggle_code.code(sql_query_formatted, language="sql")
    
    with container.spinner("Retrieving data..."):
        widget_table_result(container, sql_query)


def widget_table_result(container, sql_query):

    try:
        data = query_database(sql_query)
    except Exception as e:
        container.error(f"An error occurred: {e}")
        return

    container.dataframe(data, use_container_width=True, hide_index=True)



def widget_select_project_table(container):
    
    project_tables = {
        "ARBO":["COMBINED"],
        "RESPAT":["COMBINED"]
    }

    project_name = {
        "ARBO": "Arboviroses",
        "RESPAT": "Respiratórios"
    }

    container.title("Tables")

    project = container.selectbox(
        "Project", 
        ["ARBO", "RESPAT"], 
        label_visibility = 'collapsed',
        key = "project_table"
    )

    table = container.radio(
        f"**{project_name[project]}**",
        options=project_tables[project],
        key=f"tables_{project}"
    )

    return project, table

def widget_configs(container):

    configs_container = container.expander("# :gear: Configs")

    # maximum number of lines 100
    max_num_lines = configs_container.number_input("Máx number of lines", min_value=1, step=1, value=500)

    return {
        "max_num_lines": max_num_lines
    }

if __name__ == "__main__":
    # Streamlit UI
    st.title("🤖 Monit Chat :dna:")
    sidebar = st.sidebar

    widget_query(st)

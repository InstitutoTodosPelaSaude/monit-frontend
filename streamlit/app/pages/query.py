import streamlit as st
import sqlparse

import os
import json
from openai import OpenAI

import duckdb

import streamlit as st
import requests

QUERY_API_URL = "http://query:8000"
TTL_CACHE_DATA = 5*60 # 5 Minutes

# ====================================
# DATABASE CONNECTION AND QUERY
# ====================================

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

@st.cache_data(ttl=TTL_CACHE_DATA)
def query_database(sql_query):

    conn = get_connection()
    df = conn.execute(sql_query).fetchdf()

    return df


# ====================================
# CREATE AND FORMAT SQL QUERIES
# ====================================

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
    

# ====================================
# UI WIDGETS
# ====================================

def widget_query(container):

    # Project selection and Query Configuration
    project, table = widget_select_project_and_table(st.sidebar)
    st.sidebar.divider()
    configs = widget_configs(st.sidebar)

    container.markdown(f"Ask me anything about table **{table}** of **{project}**")

    # Question input
    col_question, col_button_confirm = container.columns( [ 4, 1 ] )

    question       = col_question.text_input("", label_visibility = 'collapsed')
    button_confirm = col_button_confirm.button(":arrow_forward:")

    # Check if the button confirm was pressed
    if not button_confirm:
        return

    st.session_state.edit_mode = False

    # Check if a valid question was inputed
    if not question.strip():
        return

    sql_query = None
    sql_query, sql_raw_query = fetch_sql_query(question, project, configs=configs)

    if not sql_query:
        st.error("Unable to generate a query for the above question. This is probabbly due a bug or momentary instabilities.")
        return

    widget_show_sql_query(container, sql_query, sql_raw_query, configs)

@st.fragment
def widget_show_sql_query(container, sql_query, sql_raw_query, configs):
    container.divider()
    container.markdown("### Results")

    sql_raw_query_formatted = sqlparse.format(sql_raw_query, reindent=True, keyword_case='upper')

    expander_query_code = container.expander("Query", False)

    if not st.session_state.edit_mode:
        # If not in edit mode, show the raw query created by the AI
        expander_query_code.code(sql_raw_query_formatted, language="sql")
        sql_raw_query_edited = sql_raw_query_formatted
    else:
        # If in edit mode, create a text area to allow the user to edit the generated query
        sql_raw_query_edited = expander_query_code.text_area(
            value=sql_raw_query_formatted, 
            label="sql_query", 
            label_visibility="collapsed"
        )

    # EDIT AND RUN QUERY
    col_button_edit, col_button_run, _ = expander_query_code.columns([1,1,8])
    button_edit = col_button_edit.button(":pencil:", help='Edit')
    button_run  = col_button_run.button(":arrow_forward:", help="Execute")

    # If edit button was pressed, change to edit mode
    if button_edit:
        st.session_state.edit_mode = True
        st.rerun(scope="fragment")
        return

    # If is in edit mode, only proceed with query execution if the RUN button was pressed
    if button_run:
        # Update the sql_query with the new edited query
        sql_query, sql_raw_query = format_sql_query(sql_raw_query_edited, configs)
    
    with container.spinner("Retrieving data..."):
        widget_query_database(container, sql_query)

def widget_query_database(container, sql_query):

    try:
        data = query_database(sql_query)
    except Exception as e:
        container.error(f"An error occurred: {e}")
        return

    container.dataframe(data, use_container_width=True, hide_index=True)


def widget_select_project_and_table(container):
    
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

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    st.title("🤖 Monit Chat :dna:")
    widget_query(st)
    st.sidebar.page_link("main.py", label="Home", icon="⬅️")

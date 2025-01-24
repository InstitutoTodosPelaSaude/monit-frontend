import streamlit as st

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from page_widgets.query_generator import widget_select_project_and_table
from models.query_generator import fetch_datadict

import streamlit as st

def widget_get_table_datadict(container):
    project, table = widget_select_project_and_table(st.sidebar)
    table = table.lower()
    datadict = fetch_datadict(project, table)['data_dictonary']

    formatted_datadict = {
        "Name": [ column_data[0] for column_data in datadict ],
        "Type": [ column_data[1] for column_data in datadict ],
        "Description": [ column_data[2] for column_data in datadict ]
    }

    container.table(
        formatted_datadict
    )

if __name__ == "__main__":

    st.title("Data Dictionary")
    widget_get_table_datadict(st)

    st.sidebar.divider()
    st.sidebar.page_link("pages/query.py", label="Monit Chat", icon="🤖")
    st.sidebar.page_link("main.py", label="Home", icon="⬅️")

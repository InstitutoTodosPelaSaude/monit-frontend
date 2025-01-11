import streamlit as st

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from page_widgets.query_generator import widget_query

import streamlit as st

TTL_CACHE_DATA = 5*60 # 5 Minutes

if __name__ == "__main__":
    # Streamlit UI

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    st.title("🤖 Monit Chat :dna:")
    widget_query(st)
    st.sidebar.page_link("main.py", label="Home", icon="⬅️")

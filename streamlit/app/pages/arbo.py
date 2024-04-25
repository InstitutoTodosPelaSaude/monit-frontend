
# this file streamlit/app/pages/arbo.py
# import path streamlit/widgets/monitoramento.py
# add this path

import streamlit as st
from pathlib import Path
import sys

path = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(path)

st.write(path)

from widgets.monitoramento import UploadFilesWidget
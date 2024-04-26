import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from page_widgets.monitoramento import UploadFilesWidget

fl = UploadFilesWidget(st, key='1')
fl.render()
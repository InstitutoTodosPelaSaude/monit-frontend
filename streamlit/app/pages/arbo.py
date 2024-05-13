import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from page_widgets.monitoramento import UploadFilesWidget

ROOT_PATH = '/data/arbo/data/'
LABS = ['dbmol', 'einstein', 'fleury', 'hilab', 'hlagyn', 'sabin']


upload_files_wdg = UploadFilesWidget(
    st, 
    key='upload_files_arbo', 
    base_path=ROOT_PATH, 
    labs=LABS
)
upload_files_wdg.render()


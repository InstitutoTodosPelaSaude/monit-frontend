import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from page_widgets.monitoramento import UploadFilesWidget
from page_widgets.monitoramento import DownloadMatricesWidget

ROOT_PATH = '/data/arbo/data/'
LABS = ['dbmol', 'einstein', 'fleury', 'hilab', 'hlagyn', 'sabin']


upload_files_wdg = UploadFilesWidget(
    st, 
    key='upload_files_arbo', 
    base_path=ROOT_PATH, 
    labs=LABS
)
upload_files_wdg.render()

download_matrices_wdg = DownloadMatricesWidget(
    st, 
    key='download_matrices_arbo', 
    base_path=ROOT_PATH, 
    labs=LABS
)
download_matrices_wdg.render()
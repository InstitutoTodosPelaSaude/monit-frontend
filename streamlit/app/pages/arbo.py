import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from page_widgets.monitoramento import UploadFilesWidget
from page_widgets.monitoramento import DownloadMatricesAndCombinedWidget
from page_widgets.monitoramento import ListFilesInLabFoldersWidget
from page_widgets.monitoramento import ListFilesInTrashFoldersWidget
from page_widgets.monitoramento import LastRunOfEachLabInfoWidget

ROOT_PATH = '/data/arbo/data/'
LABS = ['dbmol', 'einstein', 'fleury', 'hilab', 'hlagyn', 'sabin']

st.title("Central Arbo")

upload_files_wdg = UploadFilesWidget(
    st, 
    key='upload_files_arbo', 
    base_path=ROOT_PATH, 
    labs=LABS
)


download_matrices_wdg = DownloadMatricesAndCombinedWidget(
    st, 
    key='download_matrices_arbo', 
    base_path=ROOT_PATH, 
    labs=LABS
)

list_files_in_lab_folders = ListFilesInLabFoldersWidget(st, base_path=ROOT_PATH, labs=LABS)

list_files_in_trash_folders = ListFilesInTrashFoldersWidget(st, base_path=ROOT_PATH, labs=LABS)

last_run_of_each_lab = LastRunOfEachLabInfoWidget(st, base_path=ROOT_PATH, labs=LABS)

upload_files_wdg.render()
download_matrices_wdg.render()
list_files_in_lab_folders.render()
list_files_in_trash_folders.render()
last_run_of_each_lab.render()
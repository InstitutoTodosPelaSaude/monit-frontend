import streamlit as st
from pathlib import Path
import sys
import os

sys.path.append(str(Path(__file__).resolve().parent.parent))

from page_widgets.monitoramento import UploadFilesWidget
from page_widgets.monitoramento import DownloadMatricesAndCombinedWidget
from page_widgets.monitoramento import ListFilesInLabFoldersWidget
from page_widgets.monitoramento import ListFilesInTrashFoldersWidget
from page_widgets.monitoramento import LastRunOfEachLabInfoWidget
from page_widgets.monitoramento import DagsterLinkWidget
from page_widgets.monitoramento import LinkToHomeWidget
from page_widgets.monitoramento import ITPSFooterWidget

ROOT_PATH = '/data/arbo/data/'

DB_USER                  = os.getenv("DB_ARBO_USER")
DB_PASSWORD              = os.getenv("DB_ARBO_PASSWORD")
DB_HOST                  = os.getenv("DB_ARBO_HOST")
DB_PORT                  = os.getenv("DB_ARBO_PORT")
DB_DATABASE              = os.getenv("DB_ARBO_DATABASE")
DB_SCHEMA                = 'arboviroses'

DB_DAGSTER_ARBO_HOST     = os.getenv("DB_DAGSTER_ARBO_HOST")
DB_DAGSTER_ARBO_PORT     = os.getenv("DB_DAGSTER_ARBO_PORT")
DB_DAGSTER_ARBO_USER     = os.getenv("DB_DAGSTER_ARBO_USER")
DB_DAGSTER_ARBO_PASSWORD = os.getenv("DB_DAGSTER_ARBO_PASSWORD")
DB_DAGSTER_ARBO_DATABASE = os.getenv("DB_DAGSTER_ARBO_DATABASE")

DASGSTER_LINK            = os.getenv("ARBO_DAGSTER_LINK")

LABS = ['dbmol', 'einstein', 'fleury', 'hilab', 'hlagyn', 'sabin', 'target', 'hpardini']

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

last_run_of_each_lab = LastRunOfEachLabInfoWidget(
    st, 
    base_path=ROOT_PATH, 
    labs=LABS,
    dw_database_connection_kwargs={
        'user': DB_USER,
        'password': DB_PASSWORD,
        'host': DB_HOST,
        'port': DB_PORT,
        'database': DB_DATABASE,
        'default_schema': DB_SCHEMA
    },
    dagster_database_connection_kwargs={
        'user': DB_DAGSTER_ARBO_USER,
        'password': DB_DAGSTER_ARBO_PASSWORD,
        'host': DB_DAGSTER_ARBO_HOST,
        'port': DB_DAGSTER_ARBO_PORT,
        'database': DB_DAGSTER_ARBO_DATABASE
    }
)

labs_dagster_link = DagsterLinkWidget(st, dagster_link=DASGSTER_LINK)

link_to_home = LinkToHomeWidget(st)

footer = ITPSFooterWidget(st, ROOT_PATH[:-5])

upload_files_wdg.render()
download_matrices_wdg.render()
list_files_in_lab_folders.render()
list_files_in_trash_folders.render()
last_run_of_each_lab.render()
labs_dagster_link.render()
link_to_home.render()
footer.render()

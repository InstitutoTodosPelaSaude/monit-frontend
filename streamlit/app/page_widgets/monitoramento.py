from pathlib import Path
import sys

from .base import BaseWidget
from models.filesystem import FileSystem
from models.database import DWDatabaseInterface, DagsterDatabaseInterface
from collections import defaultdict
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

class UploadFilesWidget(BaseWidget):

    def __init__(
            self, 
            container, 
            key=None, 
            base_path='/', 
            labs=[]
    ):
        super(UploadFilesWidget, self).__init__(container, key)
        self.base_path = base_path
        self.labs = labs
        self.file_system = FileSystem(base_path)

    def render(self):
        
        self.container.markdown("## :arrow_up: Upload de dados")
        selected_lab = self.container.selectbox(
            'Laboratório', 
            self.labs
        )

        if selected_lab is None:
            self.container.divider()
            return
        
        selected_lab = selected_lab.lower()
        uploaded_files = self.container.file_uploader(
            "Selecione os arquivos", 
            accept_multiple_files = True,
            type=['csv', 'xlsx', 'xls', 'tsv']
        )

        self.container.divider()

        if uploaded_files is None or len(uploaded_files) == 0:
            return
        
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_content = uploaded_file.getbuffer()
            
            success = self.file_system.save_content_in_file(selected_lab, file_content, file_name)
            self.container.success(success)

            if success:
                self.container.success(f'Arquivo {file_name} salvo com sucesso!')
            else:
                self.container.error(f'Erro ao salvar arquivo {file_name}!')


class ListFileInPathWidget(BaseWidget):

    def __init__(
            self, 
            container, 
            key=None, 
            base_path='/',
            folder_path='.',
            accepted_extensions=None
    ):
        super(ListFileInPathWidget, self).__init__(container, key)
        self.base_path = base_path
        self.accepted_extensions = accepted_extensions
        self.folder_path = folder_path
        self.file_system = FileSystem(base_path)

    def render(self):
        container = self.container.expander(f":file_folder: {self.folder_path}")
        files = self.file_system.list_files_in_relative_path(self.folder_path, self.accepted_extensions)

        if len(files) == 0:
            container.text('Nenhum arquivo encontrado!')
            return
        
        for filename in files:
            filename = str(filename).split('/')[-1]

            col_filename, col_buttons = container.columns([.7, .3])
            col_date, col_download, _ = col_buttons.columns([.3, .3, .3])

            col_filename.markdown(f'**{filename}**')
            col_date.markdown(f'1d 24h')
            col_download.markdown(f':arrow_down:')


class DownloadMatricesAndCombinedWidget(BaseWidget):

    def __init__(
            self, 
            container, 
            key=None, 
            base_path='/', 
            labs=[]
    ):
        super(DownloadMatricesAndCombinedWidget, self).__init__(container, key)
        self.base_path = base_path
        self.labs = labs
        self.file_system = FileSystem(base_path)


    def render(self):
        relative_path = 'matrices/'
        accepted_extensions = ['.tsv', '.csv']

        self.container.markdown("## :1234: Matrizes")
        
        container = self.container.expander(f":file_folder: **Arquivos**")
        file_contents = self.file_system.read_all_files_in_folder_as_dataframe(relative_path, accepted_extensions)

        if len(file_contents) == 0:
            container.text('Nenhum arquivo encontrado!')
            return
        
        for filename, file_content, file_creation_time in file_contents:
            filename = str(filename).split('/')[-1]

            col_filename, col_buttons = container.columns([.7, .3])
            col_date, col_download, _ = col_buttons.columns([.3, .3, .3])

            col_filename.markdown(filename)

            if file_creation_time < 60:
                duration = f"{file_creation_time:.0f}s"
            elif file_creation_time < 3600:
                duration = f"{file_creation_time//60:.0f}m"
            elif file_creation_time < 86400:
                duration = f"{file_creation_time//3600:.0f}h"
            else:
                days = file_creation_time//86400
                hours = (file_creation_time%86400)//3600
                duration = f"{days}d {hours}h"
            
            col_date.markdown(duration)

            col_download.download_button(
                label = ":arrow_down:",
                data = file_content,
                file_name = filename,
                mime = "text/csv",
                help = "Download",
                key = f"download_{self.base_path}_{filename}"
            )

        self.add_button_download_matrices()
        self.add_button_download_combined()
        self.container.divider()


    def add_button_download_matrices(self):
        
        zip_file_content, zip_file_name = self.file_system.get_path_contents_as_zip_file('matrices/', ['.tsv', '.csv'])

        self.container.download_button(
            label = ":arrow_double_down: Download All",
            data = zip_file_content,
            file_name = zip_file_name,
            mime = "application/zip",
            help = "Download todos",
            key = f"download_all_matrices_{self.base_path}"
        )

    def add_button_download_combined(self):
        
        combined_content = self.file_system.get_file_content_as_io_bytes('combined/combined.zip')

        if combined_content is None:
            self.container.error('Não foi possível encontrar o arquivo combined.zip!')
            return

        self.container.download_button(
            label = ":arrow_down_small: Combined",
            data = combined_content,
            file_name = 'combined.zip',
            mime = "application/zip",
            help = "Download todos",
            key = f"download_all_combined_{self.base_path}"
        )


class ListFilesInLabFoldersWidget(BaseWidget):

    def __init__(
            self, 
            container, 
            key=None, 
            base_path='/', 
            labs=[]
    ):
        super(ListFilesInLabFoldersWidget, self).__init__(container, key)
        self.base_path = base_path
        self.labs = labs
        self.file_system = FileSystem(base_path)

    def render(self):
        self.container.markdown("## :file_folder: Arquivos")
        
        for lab in self.labs:
            container = self.container.expander(f":file_folder: **{lab}**")
            self.add_files_in_lab_folder(container, lab)
        
        self.container.divider()

    def add_files_in_lab_folder(self, container, lab):
        relative_path = f'{lab}/'
        accepted_extensions = ['.tsv', '.csv', '.xlsx', '.xls']

        files = self.file_system.list_files_in_relative_path(relative_path, accepted_extensions)

        if len(files) == 0:
            container.text('Nenhum arquivo encontrado!')
            return
        
        expander_container = self.container.expander(f":file_folder: **{lab}**")

        for filename in files:
            filename = str(filename).split('/')[-1]

            col_filename, col_trash = expander_container.columns([.9, .1])
            
            col_filename.markdown(f':page_facing_up: {filename}')
            
            # [WIP] Implement delete file -> MOVE FILE TO _out folder (trash)
            delete_file = col_trash.button(f':wastebasket:', key=f'delete_{filename}', help='Deletar arquivo')

            if delete_file:
                if self.file_system.move_file_to_folder(lab, filename, f'{lab}/_out'):
                    self.container.success(f'Arquivo {filename} movido para a lixeira!')
                else:
                    self.container.error(f'Erro ao mover arquivo {filename} para a lixeira!')


class ListFilesInTrashFoldersWidget(BaseWidget):

    def __init__(
            self, 
            container, 
            key=None, 
            base_path='/', 
            labs=[]
    ):
        super(ListFilesInTrashFoldersWidget, self).__init__(container, key)
        self.base_path = base_path
        self.labs = labs
        self.file_system = FileSystem(base_path)

        self.selected_files = []


    def render(self):
        self.container.markdown("## :ok: Processados")
        
        for lab in self.labs:
            container = self.container.expander(f":file_folder: **{lab}**")
            self.add_files_in_lab_folder(container, lab)

        self.add_button_restore_and_delete()        
        self.container.divider()


    def add_files_in_lab_folder(self, container, lab):
        relative_path = f'{lab}/_out/'
        accepted_extensions = ['.tsv', '.csv', '.xlsx', '.xls']

        files = self.file_system.list_files_in_relative_path(relative_path, accepted_extensions)

        if len(files) == 0:
            container.text('Nenhum arquivo encontrado!')
            return
        
        expander_container = self.container.expander(f":file_folder: **{lab}**")

        for filename in files:
            filename = str(filename).split('/')[-1]
            col_filename, col_restore = expander_container.columns([.9, .1])
            col_filename.markdown(f':page_facing_up: {filename}')

            file_selected = col_restore.checkbox('', key=f'restore_{lab}_{filename}')

            if file_selected:
                self.selected_files.append((lab, filename))


    def add_button_restore_and_delete(self):

        if len(self.selected_files) == 0:
            return
        
        col_restore, col_delete, _, _ = self.container.columns([.2,.2,.4,.2])

        restore_button = col_restore.button('Restaurar', key='restore_selected_files', use_container_width=True)
        delete_button = col_delete.button('Deletar', key='delete_selected_files', type='primary', use_container_width=True)
        type_to_delete = self.container.text_input("Digite 'DELETAR' para autorizar deleção", key='type_to_delete')

        if restore_button:
            self.container.success('Arquivos restaurados com sucesso!')

            for folder, file in self.selected_files:
                self.file_system.move_file_to_folder(folder + '/_out', file, folder)

        if delete_button and type_to_delete == 'DELETAR':
            self.container.error('Arquivos deletados com sucesso!')

            for folder, file in self.selected_files:
                self.file_system.delete_file(f'{folder}/_out/{file}')


class LastRunOfEachLabInfoWidget(BaseWidget):

    def __init__(
            self, 
            container, 
            key=None, 
            base_path='/',
            labs=[],
            dw_database_connection_kwargs=None,
            dagster_database_connection_kwargs=None
    ):
        super(LastRunOfEachLabInfoWidget, self).__init__(container, key)
        self.base_path = base_path
        self.labs = labs
        self.dw_database = DWDatabaseInterface(**dw_database_connection_kwargs)
        self.dagster_database = DagsterDatabaseInterface(**dagster_database_connection_kwargs)


    def render(self):
        self.container.markdown("## :arrows_counterclockwise: Última Run")
        
        # Retrieve last run for each lab
        # format -> ID, lab, status, timestamp start, timestamp end
        last_run_per_lab = self.dagster_database.get_last_run_for_each_pipeline()

        # format -> lab (UPPERCASE), latest date
        latest_date_per_lab  = self.dw_database.get_latest_date_of_lab_data()

        # format -> lab-epiweek, test count
        lab_epiweeks_count = self.dw_database.get_number_of_tests_per_lab_in_latest_epiweeks()

        for lab in self.labs:
            container = self.container.container(border=True)
            col_name, col_status, col_last_info, col_epiweek_count = container.columns([.15, .2, .2, .45])

            # get the last run for the current lab
            last_run_per_lab = last_run_per_lab or []
            last_run_lab = filter(lambda x: x[1] == f'"lab_{lab}"', last_run_per_lab)
            last_run_lab = list(last_run_lab)

            # get the latest date of data for the current lab
            latest_date_per_lab = latest_date_per_lab or []
            latest_date_lab = filter(lambda x: x[0] == lab.upper(), latest_date_per_lab)
            latest_date_lab = list(latest_date_lab)

            col_name.markdown(f"**{lab.capitalize()}**")
            self.add_lab_last_run_status(col_status, last_run_lab)
            self.add_lab_latest_date(col_last_info, latest_date_lab)
            self.add_lab_epiweek_count_plot(lab.upper(), col_epiweek_count, lab_epiweeks_count)

        for pipeline_name in ['combined', 'matrices']:
            container = self.container.container(border=True)
            col_name, col_status, _, _ = container.columns([.15, .2, .2, .45])

            last_run_lab = filter(lambda x: x[1] == f'"{pipeline_name}"', last_run_per_lab)
            last_run_lab = list(last_run_lab)

            col_name.markdown(f"**{pipeline_name.capitalize()}**")
            self.add_lab_last_run_status(col_status, last_run_lab)
        
        self.container.divider()

    
    def add_lab_latest_date(self, container, latest_date_lab):

        if len(latest_date_lab) == 0:
            container.markdown(f"_Sem Dados_")
            return
        
        latest_date_lab = latest_date_lab[0]
        latest_date = latest_date_lab[1]
        latest_date = latest_date.strftime("%b %d")
        container.markdown(f"_Dados até {latest_date}_")


    def add_lab_last_run_status(self, container, last_run_lab):

        if len(last_run_lab) == 0:
            last_run_lab = [None, '?', datetime.now(), datetime.now(), None]
        else:
            last_run_lab = last_run_lab[0]

        last_run_status = last_run_lab[2]
        last_run_start = last_run_lab[3]

        STATUS_TO_EMOJI = defaultdict(lambda: ':question:')
        STATUS_TO_EMOJI['FAILURE'] = ':x:'
        STATUS_TO_EMOJI['SUCCESS'] = ':white_check_mark:'
        STATUS_TO_EMOJI['CANCELED'] = ':x:'

        status_emoji = STATUS_TO_EMOJI[last_run_status]
        run_start_time = last_run_start.strftime("%d %b %H:%M")

        container.markdown(f"{status_emoji} {run_start_time}")

    def add_lab_epiweek_count_plot(self, lab, container, lab_epiweeks_count):

        if lab_epiweeks_count == None or len(lab_epiweeks_count) == 0:
            return
        
        lab = lab.upper()
        tem_dados = False

        lab_epiweeks_count = lab_epiweeks_count.items()
        lab_epiweeks_count = [ [*lab_epiweek.split('-'), count ] for lab_epiweek, count in lab_epiweeks_count ]
        lab_epiweeks_count_df = pd.DataFrame(lab_epiweeks_count, columns=['Lab', 'Epiweek', 'Count'])
        lab_epiweeks_count_df['Lab'] = lab_epiweeks_count_df['Lab'].str.upper()
        lab_epiweeks_count_df = lab_epiweeks_count_df.query(f"Lab=='{lab}'")

        if len(lab_epiweeks_count_df) == 0:
            container.markdown(f"*Sem dados*")
            return

        # container.write(lab_epiweeks_count_df)

        df_chart_data = lab_epiweeks_count_df
        df_chart_data = df_chart_data.sort_values(by='Epiweek', ascending=True)
        fig = plt.figure( figsize=(10, 1) )
        # remove border
        fig.gca().spines['top'].set_visible(False)
        fig.gca().spines['right'].set_visible(False)
        fig.gca().spines['left'].set_visible(False)
        ax = df_chart_data.plot(
            x='Epiweek', 
            y='Count', 
            kind='bar', 
            ax=fig.gca(), 
            color='#00a6ed',
            # bar width
            width=0.5
        )
        # remove y-label
        ax.set_ylabel('')
        ax.set_xlabel('')
        # remove legend
        ax.get_legend().remove()
        # increase x-ticks font size
        ax.tick_params(axis='x', labelsize=20)
        # remove y-ticks
        ax.set_yticks([])
        # add the value on top of each bar
        for p in ax.patches:
            if p.get_height() <= 0:
                continue
            tem_dados = True
            ax.annotate(
                f"{p.get_height()}",
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center',
                va='center',
                fontsize=16,
                color='black',
                xytext=(0, 10),
                textcoords='offset points'
            )

        if not tem_dados:
            container.markdown(f"*Sem dados*")
            return
        container.pyplot(fig)


class DagsterLinkWidget(BaseWidget):

    def __init__(
            self, 
            container, 
            key=None, 
            dagster_link=""
    ):
        super(DagsterLinkWidget, self).__init__(container, key)
        self.dagster_link = dagster_link

    def render(self):
        self.container.link_button(
            "**Acessar o Dagster :octopus:**", 
            self.dagster_link, 
            use_container_width=True
        )

class LinkToHomeWidget(BaseWidget):

    def __init__(
            self, 
            container, 
            key=None
    ):
        super(LinkToHomeWidget, self).__init__(container, key)

    def render(self):
        self.container.page_link("main.py", label="Home", icon="⬅️")

class ITPSFooterWidget(BaseWidget):

    def __init__(
            self, 
            container,
            file_path, 
            key=None
    ):
        super(ITPSFooterWidget, self).__init__(container, key)
        self.file_path = file_path

    def render(self):
        file_content = self.read_version_file()

        try:
            commit_hash, commit_date = file_content.split(' ')
        except:
            commit_hash, commit_date = 'UNK_COMMIT', 'UNK_DATE'

        self.container.write("#")
        self.container.divider()
        self.container.markdown(f"DEVELOPED BY [ITpS](https://www.itps.org.br/). lc-{commit_hash}, {commit_date}.")


    def read_version_file(self):
        file_content = "UNK_COMMIT UNK_DATE"
        try:
            with open(self.file_path + 'version.txt', 'r') as file:
                file_content = file.read()
        except:
            pass

        return file_content
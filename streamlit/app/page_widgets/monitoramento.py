from pathlib import Path
import sys

from .base import BaseWidget
from models.filesystem import FileSystem

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
        
        zip_file_content, zip_file_name = self.file_system.get_path_contents_as_zip_file('combined/', ['.tsv', '.csv'])

        self.container.download_button(
            label = ":arrow_down_small: Combined",
            data = zip_file_content,
            file_name = zip_file_name,
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
        accepted_extensions = ['.tsv', '.csv', '.xslx', '.xls']

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
        accepted_extensions = ['.tsv', '.csv', '.xslx', '.xls']

        files = self.file_system.list_files_in_relative_path(relative_path, accepted_extensions)

        if len(files) == 0:
            container.text('Nenhum arquivo encontrado!')
            return
        
        expander_container = self.container.expander(f":file_folder: **{lab}**")

        for filename in files:
            filename = str(filename).split('/')[-1]
            col_filename, col_restore = expander_container.columns([.9, .1])
            col_filename.markdown(f':page_facing_up: {filename}')

            file_selected = col_restore.checkbox('', key=f'restore_{filename}')

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
            labs=[]
    ):
        super(LastRunOfEachLabInfoWidget, self).__init__(container, key)
        self.base_path = base_path
        self.labs = labs
        self.file_system = FileSystem(base_path)

    def render(self):
        self.container.markdown("## :arrows_counterclockwise: Última execução [WIP]")
        
        for lab in self.labs:
            container = self.container.container(border=True)
            self.add_lab_last_run(container, lab)
        
        self.container.divider()

    def add_lab_last_run(self, container, lab):
        col_name, col_status, col_last_info, col_epiweek_count = container.columns([.15, .2, .2, .45])
        col_name.markdown(f"**{lab}**")

        self.add_lab_last_run_status(col_status, lab)

    def add_lab_last_run_status(self, container, lab):
        container.markdown(f":white_check_mark: 14 May 22:28")
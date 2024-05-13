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

class DownloadMatricesWidget(BaseWidget):

    def __init__(
            self, 
            container, 
            key=None, 
            base_path='/', 
            labs=[]
    ):
        super(DownloadMatricesWidget, self).__init__(container, key)
        self.base_path = base_path
        self.labs = labs
        self.file_system = FileSystem(base_path)

    def render(self):
        relative_path = 'matrices/'

        self.container.markdown("## :1234: Download de matrizes")
        
        container = self.container.expander(f":file_folder: **Arquivos**")
        files = self.file_system.list_files_in_relative_path(relative_path, ['.tsv', '.csv'])

        if len(files) == 0:
            container.text('Nenhum arquivo encontrado!')
            return
        
        for filename in files:
            filename = str(filename).split('/')[-1]

            col_filename, col_buttons = container.columns([.7, .3])
            col_date, col_download, _ = col_buttons.columns([.3, .3, .3])

            col_filename.markdown(f'{filename}')
            col_date.markdown(f'1d 24h')
            col_download.markdown(f':arrow_down:')

        self.container.divider()
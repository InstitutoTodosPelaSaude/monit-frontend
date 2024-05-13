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
            return
        
        selected_lab = selected_lab.lower()
        uploaded_files = self.container.file_uploader(
            "Selecione os arquivos", 
            accept_multiple_files = True,
            type=['csv', 'xlsx', 'xls', 'tsv']
        )

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

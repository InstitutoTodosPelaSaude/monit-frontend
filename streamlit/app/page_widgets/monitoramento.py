from pathlib import Path
import sys

from .base import BaseWidget

class UploadFilesWidget(BaseWidget):

    def __init__(self, container, key=None, base_path='/', labs=[]):
        super(UploadFilesWidget, self).__init__(container, key)
        self.base_path = base_path
        self.labs = labs

    def render(self):
        self.container.title("Upload de Dados")
        self.container.write("Faça upload ... arquivos necessários para o monitoramento.")

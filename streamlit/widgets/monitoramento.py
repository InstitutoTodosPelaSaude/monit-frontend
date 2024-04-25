from pathlib import Path
import sys

from .base import BaseWidget

class UploadFilesWidget(BaseWidget):
    def __init__(self, container, key=None, labs=[]):
        super().__init__(container, key)

    def render(self):
        return self.container.upload_files(self.key)
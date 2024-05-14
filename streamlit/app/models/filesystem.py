import io
from pathlib import Path
import pandas as pd
from datetime import datetime
import io
import zipfile

class FileSystem():
    _instance = None

    # [WIP] Make this class a singleton
    def __init__(self, root_path: str):
        self.root_path = root_path

    def list_files_in_relative_path(self, relative_path, accepted_extensions=None):
        absolute_path = Path(self.root_path) / relative_path
        
        all_files = absolute_path.iterdir()

        if accepted_extensions:
            return [file for file in all_files if file.suffix in accepted_extensions]
        return all_files
    
    def save_content_in_file(self, relative_path, content, file_name):
        absolute_path = Path(self.root_path) / relative_path
        try:
            with open(absolute_path / file_name, 'wb') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f'Error saving content in file: {e}')
            return False
        

    def read_all_files_in_folder_as_dataframe(self, relative_path, accepted_extensions=None):
        files = self.list_files_in_relative_path(relative_path, accepted_extensions)
        files.sort()
        file_contents = [
            (file, pd.read_csv(file).to_csv(index=False).encode('utf-8') )
            for file in files
        ]
        return file_contents
import io
from pathlib import Path

class FileSystem():
    _instance = None

    # [WIP] Make this class a singleton
    def __init__(self, root_path: str):
        self.root_path = root_path

    def list_files_in_relative_path(self, relative_path, accepted_extensions=None):
        absolute_path = Path(self.root_path) / relative_path
        all_files = self.list_files_in_relative_path(absolute_path)
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
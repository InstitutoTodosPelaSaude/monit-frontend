import io
from pathlib import Path
import pandas as pd
from datetime import datetime
import os
import zipfile

from minio import Minio
from minio.error import S3Error
from minio.commonconfig import REPLACE, CopySource

class FileSystem():
    _instance = None

    # [WIP] Make this class a singleton
    def __init__(self, root_path: str, secure=False):
        """
        Wrapper to interact with the application files stored in MinIO.

        Args:
            root_path (str): Root path. /bucketname/path
        """
        self.root_path = root_path
        self.endpoint = "172.30.106.164:9000"#os.getenv("MINIO_ENDPOINT")
        self.access_key = "WaGjc772vXoOAtgtsafo"#os.getenv("MINIO_ACCESS_KEY")
        self.secret_key = "JLRzTMEuJCBWVwQnrCMjvl4Ie3Ls9Ba1rrAifnsB"#os.getenv("MINIO_SECRET_KEY")
        self.secure = secure
        self.client = None

        self.connect()


    def connect(self):
        """
        Establishes a connection to the MinIO server using the provided environment variables.
        """
        try:
            # Create a MinIO client
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )

            # Check if the bucket exists or can be accessed
            bucket_name = self.root_path.split("/")[1]  # Assuming root_path is in form /bucketname/path
            if not self.client.bucket_exists(bucket_name):
                raise S3Error(f"Bucket '{bucket_name}' does not exist or is not accessible.")

            print(f"Connected successfully to MinIO bucket: {bucket_name}")
            self.bucket_name = bucket_name
            self.root_path = "/".join( self.root_path.split("/")[2:] )
        except S3Error as e:
            self.bucket_name = None
            print(f"Error connecting to MinIO: {str(e)}")


    def list_files_in_relative_path(self, relative_path: str, accepted_extensions=None):
    
        try:
            prefix = self.root_path+relative_path
            print(prefix)

            # List objects in the specified path (prefix)
            objects = self.client.list_objects(self.bucket_name, prefix=str(prefix), recursive=False)

            # Filter files by extension if provided
            file_list = []
            for obj in objects:
                if accepted_extensions:
                    # Check if the object's extension matches the accepted extensions
                    if any(obj.object_name.endswith(ext) for ext in accepted_extensions):
                        file_list.append(obj.object_name)
                else:
                    file_list.append(obj.object_name)

            return file_list
        except S3Error as e:
            print(f"Error listing files in MinIO: {e}")
            

    def save_content_in_file(self, relative_path, content, file_name):
        try:
            if not relative_path.endswith("/"):
                relative_path += "/"
                
            object_name = self.root_path + relative_path + file_name
            object_name = str(object_name)

            self.client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(content),
                length=len(content)
            )
            
            return True
        except Exception as e:
            print(f'Error saving content in file: {e}')
            return False


    def get_file_content_as_io_bytes(self, relative_path):
        try:
            object_path = self.root_path / relative_path
            response = self.client.get_object(self.bucket_name, object_path)
            return io.BytesIO(response.read())
        except Exception as e:
            print(f'Error getting file content as io bytes: {e}')
            return None


    def read_all_files_in_folder_as_buffer(self, relative_path, accepted_extensions=None):
        files = self.list_files_in_relative_path(relative_path, accepted_extensions)
        files.sort()

        dt_now = datetime.now()
        dt_last_modification = lambda file:datetime.fromtimestamp(os.path.getmtime(file))

        try:
            file_contents = [
                (
                    file, 
                    open(file, 'rb').read(),
                    (dt_now - dt_last_modification(file)).total_seconds() # Time in seconds since last modification
                )
                for file in files
            ]

        except Exception as e:
            file_contents = [
                ('UNABLE TO READ FILE', f'Error reading file: {e}'.encode('utf-8'), 0)
                for file in files
            ]

        return file_contents
    

    def get_path_contents_as_zip_file(self, relative_path, accepted_extensions):
        file_content_list = self.read_all_files_in_folder_as_buffer(relative_path, accepted_extensions)

        zip_file_name = f"{relative_path.replace('/', '')}.zip"
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for filename, file_contents, _ in file_content_list:
                filename = str(filename).split('/')[-1]
                zip_file.writestr(filename, file_contents)

        return zip_buffer.getvalue(), zip_file_name
    

    def move_file_to_folder(self, relative_path, file_name, target_folder):
        try:
            object_name = self.root_path + relative_path + file_name
            target_object_name = self.root_path + target_folder + file_name

            object_name = str(object_name)
            target_object_name = str(target_object_name)
            self.client.copy_object(
                self.bucket_name, 
                target_object_name, 
                CopySource( self.bucket_name, object_name )
            )

            # Remove the original file
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f'Error moving file to folder: {e}')
            return False

   
    def delete_file(self, relative_path):
        absolute_path = Path(self.root_path) / relative_path

        try:
            os.remove(absolute_path)
            return True
        except Exception as e:
            print(f'Error deleting file: {e}')
            return False
        

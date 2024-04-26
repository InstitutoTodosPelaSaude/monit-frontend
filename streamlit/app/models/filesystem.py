class FileSystem():
    _instance = None

    def __new__(cls, root_path):
        if not cls._instance:
            cls._instance = super().__new__(cls, root_path)
        return cls._instance

    def __init__(self, root_path):
        self.root_path = root_path
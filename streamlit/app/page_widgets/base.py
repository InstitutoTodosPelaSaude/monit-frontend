from abc import ABC, abstractmethod
import streamlit as st

# ../models/database.py
# ../models/filesystem.py
# import these two paths

from pathlib import Path
import sys

path = str(Path(__file__).resolve().parent.parent)
sys.path.append(path)

from models.database import DWDatabaseInterface
from models.filesystem import FileSystem

class BaseWidget(ABC):
    """The base class for all Streamlit widgets."""

    file_system = FileSystem

    def __init__(self, container=st, key=None):
        self.key = key
        self.container = container

    @abstractmethod
    def render(self):
        """Renders the widget."""
        pass

from typing import Optional
import requests
import os
import mimetypes

class Client:
    def __init__(self, url="http://localhost:8000"):
        self.url = url
    
        
    def _file_path_dict(self, files: dict) -> dict:
        created_dict = {}
        for name in files:
            filepath = files[name]
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
  
            mime_type, _ = mimetypes.guess_type(filepath)
            mime_type = mime_type or "application/octet-stream"

            file_obj = open(filepath, "rb")
            filename = os.path.basename(filepath)
            created_dict[name] = (filename, file_obj, mime_type)
        return created_dict

    def post(self, endpoint: str, data: dict):
        response = requests.post(f"{self.url}/{endpoint}", json=data)
        return response.json()
    
    # post with files and json
    def post_files(self, endpoint: str, files: dict, data: Optional[dict] = None):
        file_dict = self._file_path_dict(files)
        response = requests.post(f"{self.url}/{endpoint}", files=file_dict, data=data)
        return response.json()
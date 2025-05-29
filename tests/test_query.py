import os
from pathlib import Path
from libs.Client import Client
from libs.util import dd
import mimetypes


script_dir = os.path.dirname(os.path.abspath(__file__))
    
# function to scan a local directory for files,
# return a list of files with full paths recursively
def listdir(path):    
    files = []
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            full_path = str(Path(root) / filename)
            # add file name, full path, mimetype to a dictionary
            file_data = {
                "name": filename,
                "path": full_path,
                "mimetype": mimetypes.guess_type(full_path) or '' # mimetype from file extension
            }
            files.append(file_data)
    return files

    
def test_query():
    client = Client()
    for file in listdir(f"{script_dir}/data"):
        response = client.post_files(
            endpoint="/ingest",
            data={"path" : file['path']},
            files={"file":file["path"]}
        )
        assert "doc_id" in response
        
    response = client.post(
        endpoint="/query",
        data={
            "query": "What is the capital of France?",
            "page_size": 5
        })
    required_keys = {"doc_id", "path"}

    for item in response:
        assert required_keys.issubset(item), f"Missing keys in item: {item}"

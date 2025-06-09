# function to debug and print the

import hashlib
import uuid
from fastapi import UploadFile
import os
from pathlib import Path
import mimetypes
from app.config import TEMP_STORAGE
from models import FileInfo


def dd(*args):
    print("DEBUG:", *args)
    exit()
    
def uploaded_file_to_local(uploadfile: UploadFile, filename=str(uuid.uuid4())):
    # guess extension
    if uploadfile.filename is None:
        raise ValueError("Filename is required for the uploaded file.")
    extension = uploadfile.filename.split(".")[-1] if "." in uploadfile.filename else "bin"
    
    extension = "." + extension
    local_filename = f"{TEMP_STORAGE}/{filename}{extension}"
    
    with open(local_filename, "wb") as f:
        f.write(uploadfile.file.read())
    
    return local_filename
    
def list_files(path:str)-> list[FileInfo]:
    files = []
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            full_path = str(Path(root) / filename)
            # add file name, full path, mimetype to a dictionary
            file_data = {
                "name": filename,
                "path": full_path,
                "mimetype": mimetypes.guess_type(full_path)[0] or '' # mimetype from file extension
            }
            files.append(file_data)
    return files
    
def chunk_text_words(text, chunk_size=100, overlap=20):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i + chunk_size]
        chunks.append(' '.join(chunk))

    return chunks

def text_to_hash(text, algorithm='sha256'):
    # Create a hash object
    hash_object = hashlib.new(algorithm)

    # Update the hash object with the bytes of the text
    hash_object.update(text.encode('utf-8'))

    # Get the hexadecimal digest of the hash
    hex_dig = hash_object.hexdigest()

    return hex_dig
    

def human_time(dt):
    hour = dt.hour

    if 0 <= hour < 3:
        return "late night"
    elif 3 <= hour < 5:
        return "midnight"
    elif 5 <= hour < 8:
        return "early morning"
    elif 8 <= hour < 12:
        return "morning"
    elif 12 <= hour < 14:
        return "noon"
    elif 14 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 20:
        return "evening"
    elif 20 <= hour < 23:
        return "night"
    else:
        return "late night"
    
def human_date(dt):
    return dt.strftime("%A %B %Y")
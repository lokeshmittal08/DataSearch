from pathlib import Path
import textract

def load_documents(folder_path: Path):
    folder_path = Path(folder_path)
    documents = []
    print(f"Looking for documents in: {folder_path}")
    for file_path in folder_path.glob("**/*"): #folder_path.glob("**/*"):
        print(f"Looking for documents in: {folder_path}")
        if file_path.suffix.lower() in [".pdf", ".docx", ".txt"]:
            try:
                text = textract.process(str(file_path)).decode("utf-8")
                documents.append({
                    "file_path": str(file_path),
                    "content": text
                })
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")
    print(f"Total documents loaded: {len(documents)}")            
    return documents
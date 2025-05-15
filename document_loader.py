from pathlib import Path
import textract
import pytesseract
from pdf2image import convert_from_path
import tempfile

def extract_text_with_ocr(pdf_path):
    text = ""
    try:
        images = convert_from_path(pdf_path)
        for i, image in enumerate(images):
            ocr_text = pytesseract.image_to_string(image)
            text += ocr_text + "\n"
    except Exception as e:
        print(f"OCR failed for {pdf_path}: {e}")
    return text

def load_documents(folder_path: Path):
    folder_path = Path(folder_path)
    documents = []
    print(f"Looking for documents in: {folder_path}")

    for file_path in folder_path.glob("**/*"):
        if file_path.suffix.lower() in [".pdf", ".docx", ".txt"]:
            try:
                text = textract.process(str(file_path)).decode("utf-8").strip()
                if not text:
                    raise ValueError("Empty text from textract")
            except Exception as e:
                print(f"Textract failed for {file_path}, trying OCR: {e}")
                if file_path.suffix.lower() == ".pdf":
                    text = extract_text_with_ocr(file_path)
                else:
                    text = ""

            if text.strip():
                documents.append({
                    "file_path": str(file_path),
                    "content": text
                })
            else:
                print(f"No text found in {file_path} even after OCR.")

    print(f"Total documents loaded: {len(documents)}")
    return documents

import os
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

def extract_with_docling(pdf_path):

    try:
        converter = DocumentConverter()
        result: DocumentStream = converter.convert(pdf_path)
        markdown = result.document.export_to_markdown()
        if "<!-- image -->" in markdown or not markdown.strip():
            print("[Docling] Detected image-based content. Falling back.")
            return None
        print("[Docling] Successfully extracted content.")
        return markdown
    except Exception as e:
        print(f"[Docling] Failed: {e}")
        return None

def extract_with_pdfplumber(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if not text.strip():
            print("[pdfplumber] No text found. Falling back.")
            return None
        print("[pdfplumber] Successfully extracted content.")
        return text
    except Exception as e:
        print(f"[pdfplumber] Failed: {e}")
        return None

def extract_with_ocr(pdf_path):
    try:
        print("[OCR] Converting pages to images...")
        images = convert_from_path(pdf_path)
        text = ""
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            text += f"\n\n=== Page {i+1} ===\n{page_text}"
        print("[OCR] Extraction complete.")
        return text
    except Exception as e:
        print(f"[OCR] Failed: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    for extractor in [extract_with_docling, extract_with_pdfplumber, extract_with_ocr]:
        text = extractor(pdf_path)
        if text:
            return text
    print("[ERROR] All extraction methods failed.")
    return None

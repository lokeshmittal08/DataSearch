from pathlib import Path
import textract
#import pytesseract
from pdf2image import convert_from_path
from PIL import Image,ImageEnhance
import pytesseract
import pdfplumber
import logging
import fitz
import subprocess
import os
import ocrmypdf
import platform
import shutil

def check_dependencies() -> bool:
    """Check if Poppler and Tesseract are installed and in PATH."""
    try:
        subprocess.run(["pdftoppm", "-v"], capture_output=True, check=True)
        print("Poppler (pdftoppm) found in PATH")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Poppler (pdftoppm) not found in PATH. Install Poppler and add to PATH.")
        return False

    try:
        subprocess.run(["tesseract", "--version"], capture_output=True, check=True)
        print("Tesseract found in PATH")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Tesseract not found in PATH. Install Tesseract and add to PATH.")
        return False

    return True

def repair_pdf(file_path: Path, output_dir: Path) -> Path:
    """Attempt to repair a PDF using PyMuPDF."""
    try:
        output_pdf = output_dir / f"{file_path.stem}_repaired.pdf"
        with fitz.open(file_path) as pdf:
            pdf.save(output_pdf)
        print(f"Repaired PDF saved as {output_pdf}")
        return output_pdf
    except Exception as e:
        print(f"Failed to repair {file_path}: {e}")
        return file_path
def debug_pdf_structure(file_path: Path) -> dict:
    """Inspect PDF structure, metadata, and security settings."""
    try:
        with fitz.open(file_path) as pdf:
            metadata = pdf.metadata
            page_count = pdf.page_count
            is_image_based = any(page.get_images(full=True) for page in pdf)
            is_protected = getattr(pdf, 'isLocked', False) or pdf.needs_pass
            return {
                "metadata": metadata,
                "page_count": page_count,
                "is_image_based": is_image_based,
                "is_protected": is_protected
            }
    except Exception as e:
        print(f"Failed to debug PDF structure for {file_path}: {e}")
        return {"error": str(e)}
    
def extract_text_with_textract(file_path: Path) -> str:
    """Attempt to extract text from a PDF using textract."""
    try:
        text = textract.process(str(file_path)).decode("utf-8").strip()
        if text:
            print(f"Textract succeeded: {file_path}")
            return text
        else:
            print(f"Textract returned empty text for {file_path}")
            return ""
    except Exception as e:
        print(f"Textract failed for {file_path}: {e}")
        return ""

def extract_text_with_pdfplumber(file_path: Path) -> str:
    """Attempt to extract text from a PDF using pdfplumber."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "".join(page.extract_text() or "" for page in pdf.pages).strip()
        if text:
            print(f"pdfplumber succeeded: {file_path}")
            return text
        else:
            print(f"pdfplumber returned empty text for {file_path}")
            return ""
    except Exception as e:
        print(f"pdfplumber failed for {file_path}: {e}")
        return ""

def extract_text_with_ocr(file_path: Path, output_dir: Path) -> str:
    """Convert PDF to images and extract text using OCR."""
    if not check_dependencies():
        print(f"OCR skipped for {file_path}: Missing Poppler or Tesseract")
        return ""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        images = convert_from_path(file_path, dpi=400, output_folder=output_dir, fmt="png")
        text = ""
        for i, image_path in enumerate(images):
            try:
                image = Image.open(image_path).convert("RGB")
                image = preprocess_image(image)
                debug_image_path = output_dir / f"{file_path.stem}_page_{i+1}.png"
                image.save(debug_image_path)
                page_text = pytesseract.image_to_string(image, lang="eng", config="--psm 6 --oem 1").strip()
                if page_text:
                    text += page_text + "\n"
                print(f"OCR processed page  {file_path}, saved as {debug_image_path}")
                os.remove(image_path)
            except Exception as e:
                print(f"OCR failed for page {i+1} of {file_path}: {e}")
        if text:
            print(f"OCR succeeded: {file_path}")
            return text
        else:
            print(f"OCR returned empty text for {file_path}")
            return ""
    except Exception as e:
        print(f"OCR failed for {file_path}: {e}")
        return ""

def extract_text_with_pymupdf(file_path: Path) -> str:
    """Attempt to extract text from a PDF using PyMuPDF."""
    try:
        with fitz.open(file_path) as pdf:
            text = "".join(page.get_text("text") for page in pdf).strip()
        if text:
            print(f"PyMuPDF succeeded: {file_path}")
            return text
        else:
            print(f"PyMuPDF returned empty text for {file_path}")
            return ""
    except Exception as e:
        print(f"PyMuPDF failed for {file_path}: {e}")
        return ""
def preprocess_image(image: Image.Image) -> Image.Image:
    """Preprocess image for better OCR accuracy."""
    try:
        image = image.convert("L")  # Grayscale
        image = ImageEnhance.Contrast(image).enhance(2.0)  # Increase contrast
        image = ImageEnhance.Brightness(image).enhance(1.2)  # Adjust brightness
        image = ImageEnhance.Sharpness(image).enhance(2.0)  # Increase sharpness
        return image
    except Exception as e:
        print(f"Image preprocessing failed: {e}")
        return image

def extract_text_with_ocr(file_path: Path, output_dir: Path) -> str:
    """Convert PDF to images and extract text using OCR."""
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        images = convert_from_path(file_path, dpi=300, output_folder=output_dir, fmt="png")
        text = ""
        for i, image_path in enumerate(images):
            try:
                image = Image.open(image_path).convert("RGB")
                image = preprocess_image(image)
                page_text = pytesseract.image_to_string(image, lang="eng").strip()
                if page_text:
                    text += page_text + "\n"
                print(f"OCR processed page {i+1} of {file_path}")
                # Clean up image file
                os.remove(image_path)
            except Exception as e:
                print(f"OCR failed for page {i+1} of {file_path}: {e}")
        if text:
            print(f"OCR succeeded: {file_path}")
            return text
        else:
            print(f"OCR returned empty text for {file_path}")
            return ""
    except Exception as e:
        print(f"OCR failed for {file_path}: {e}")
        return ""

def extract_text_with_ocrmypdf(file_path: Path, output_dir: Path) -> str:
    """Use ocrmypdf for robust OCR as a last resort."""
    try:
        output_pdf = output_dir / f"{file_path.stem}_ocr.pdf"
        ocrmypdf.ocr(str(file_path), str(output_pdf), language="eng", force_ocr=True)
        text = extract_text_with_pymupdf(output_pdf) or extract_text_with_textract(output_pdf)
        if text:
            print(f"ocrmypdf succeeded: {file_path}")
            return text
        else:
            print(f"ocrmypdf returned empty text for {file_path}")
            return ""
    except Exception as e:
        print(f"ocrmypdf failed for {file_path}: {e}")
        return ""

def try_decrypt_pdf(file_path: Path, output_dir: Path) -> Path:
    """Attempt to decrypt a protected PDF using qpdf."""
    try:
        output_pdf = output_dir / f"{file_path.stem}_decrypted.pdf"
        subprocess.run(["qpdf", "--decrypt", str(file_path), str(output_pdf)], check=True)
        print(f"Decrypted PDF: {output_pdf}")
        return output_pdf
    except Exception as e:
        print(f"Failed to decrypt {file_path}: {e}")
        return file_path    
def extract_pdf_text(file_path: Path, temp_dir: Path = Path("temp")) -> str:
    """Attempt to extract text from a PDF using multiple methods."""
 # Debug PDF structure
    debug_info = debug_pdf_structure(file_path)
    print(f"PDF debug info for {file_path}: {debug_info}")

    # Handle protected PDFs
    if debug_info.get("is_protected", False):
        print(f"Detected protected PDF: {file_path}")
        file_path = try_decrypt_pdf(file_path, temp_dir)
# Try repairing the PDF
    repaired_file_path = repair_pdf(file_path, temp_dir)
    if repaired_file_path != file_path:
        file_path = repaired_file_path
        print(f"Using repaired PDF: {file_path}")


    # Try textract
    text = extract_text_with_textract(file_path)
    if text:
        return text

    # Try pdfplumber
    text = extract_text_with_pdfplumber(file_path)
    if text:
        return text

    # Try PyMuPDF
    text = extract_text_with_pymupdf(file_path)
    if text:
        return text

    # Fallback to OCR
    text = extract_text_with_ocr(file_path, temp_dir)
    if text:
        return text
# Force OCR due to repeated text extraction failures
    print(f"All text extraction methods failed, forcing OCR for {file_path}")
    text = extract_text_with_ocr(file_path, temp_dir)
    if text:
        return text
    # Last resort: ocrmypdf
    text = extract_text_with_ocrmypdf(file_path, temp_dir)
    return text

def load_documents(folder_path: Path):
    folder_path = Path(folder_path)
    documents = []
    print(f"Looking for documents in: {folder_path}")

    for file_path in folder_path.glob("**/*"):
        if file_path.is_file():
            suffix = file_path.suffix.lower()

            if suffix in [".pdf"]:
                text = extract_pdf_text(file_path)
                if text.strip():
                    documents.append({
                        "file_path": str(file_path),
                        "content": text,
                        "type": "text"
                    })
                    print(f"Successfully extracted text from {file_path}")
                else:
                    print(f"No text extracted from {file_path}")

            elif suffix in [".docx", ".txt"]:
                try:
                    text = textract.process(str(file_path)).decode("utf-8").strip()
                    if text:
                        documents.append({
                            "file_path": str(file_path),
                            "content": text,
                            "type": "text"
                        })
                        print(f"Successfully extracted text from {file_path}")
                    else:
                        print(f"No text extracted from {file_path}")
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")

            elif suffix in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                try:
                    image = Image.open(file_path).convert("RGB")
                    # Optionally perform OCR on images
                    text = pytesseract.image_to_string(image, lang="eng").strip()
                    documents.append({
                        "file_path": str(file_path),
                        "content": text if text else image,
                        "type": "text" if text else "image"
                    })
                    print(f"Processed image {file_path}")
                except Exception as e:
                    print(f"Failed to load image {file_path}: {e}")

    print(f"Total documents loaded: {len(documents)}")
    return documents
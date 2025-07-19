from math import sin
from singleton_decorator import singleton
from docx import Document
from app.pdf_utils import extract_text_from_pdf
from libs.ImageParser import ImageParser

@singleton
class AnyFileParser:
    def __init__(self, image_parser=ImageParser()):
        self.image_parser = image_parser


    def _is_image(self, file_path: str) -> bool:
        # Check if the file is an image based on its content type or extension
        return file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
    
    def _is_pdf(self, file_path: str) -> bool:
        # Check if the file is a PDF based on its content type or extension
        return file_path.lower().endswith('.pdf')

    def _is_docx(self, file_path: str) -> bool:
        return file_path.lower().endswith('.docx')

    def _is_txt(self, file_path: str) -> bool:
        return file_path.lower().endswith('.txt')
    
    def _parse_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return text
        except Exception as e:
            raise ValueError(f"Failed to parse .docx file: {e}")

    def _parse_txt(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Failed to parse .txt file: {e}")

   
    def parse(self, file_path: str) -> str:
        if self._is_pdf(file_path):
            return extract_text_from_pdf(file_path)
        if self._is_image(file_path):
            return self.image_parser.parse(file_path)
        if self._is_docx(file_path):
            return self._parse_docx(file_path)
        if self._is_txt(file_path):
            return self._parse_txt(file_path)
        raise ValueError("Unsupported file type")
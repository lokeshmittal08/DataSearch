from math import sin
from singleton_decorator import singleton

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

    def parse(self, file_path: str) -> str:
        if self._is_pdf(file_path):
            return extract_text_from_pdf(file_path)
        if self._is_image(file_path):
            return self.image_parser.parse(file_path)
        raise ValueError("Unknown file type")
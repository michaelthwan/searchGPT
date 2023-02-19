from bs4 import BeautifulSoup

from backend.src.text_extract.abc_text_extract import AbstractTextExtractSvc


class BeautifulSoupSvc(AbstractTextExtractSvc):
    def __init__(self):
        super().__init__()

    def extract_from_html(self, html_str: str):
        soup = BeautifulSoup(html_str, "html.parser")
        return [el.get_text() for el in soup.select('p')]

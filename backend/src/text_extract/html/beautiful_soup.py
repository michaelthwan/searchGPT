from bs4 import BeautifulSoup

from text_extract.html.abc_html_extract import AbstractHtmlExtractSvc


class BeautifulSoupSvc(AbstractHtmlExtractSvc):
    def __init__(self):
        super().__init__()

    def extract_from_html(self, html_str: str):
        soup = BeautifulSoup(html_str, "html.parser")
        return [el.get_text() for el in soup.select('p')]

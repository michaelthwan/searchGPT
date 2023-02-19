from trafilatura import bare_extraction

from backend.src.text_extract.abc_text_extract import AbstractTextExtractSvc


class TrafilaturaSvc(AbstractTextExtractSvc):
    def __init__(self):
        super().__init__()

    def extract_from_html(self, html_str: str):
        extract = bare_extraction(html_str, favor_precision=True)
        return extract['text'].split("\n")

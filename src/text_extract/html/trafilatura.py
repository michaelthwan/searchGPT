from trafilatura import bare_extraction

from text_extract.html.abc_html_extract import AbstractHtmlExtractSvc


class TrafilaturaSvc(AbstractHtmlExtractSvc):
    def __init__(self):
        super().__init__()

    def extract_from_html(self, html_str: str):
        extract = bare_extraction(html_str, favor_precision=True)
        try:
            return extract['text'].split("\n")
        except:
            return []

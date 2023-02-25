from text_extract.doc.abc_doc_extract import AbstractDocExtractSvc


class PptSvc(AbstractDocExtractSvc):
    def __init__(self):
        super().__init__()

    def extract_from_doc(self, path: str):
        pass


ppt_extract_svc = PptSvc()

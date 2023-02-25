import docx
import nltk

from text_extract.doc.abc_doc_extract import AbstractDocExtractSvc


class DocxSvc(AbstractDocExtractSvc):
    def __init__(self):
        super().__init__()

    def extract_from_doc(self, path: str):
        doc_file = docx.Document(path)
        raw_text_list = [paragraph.text for paragraph in doc_file.paragraphs if len(paragraph.text) > 0]
        sentence_list = list()
        for raw_text in raw_text_list:
            sentence_list.extend(nltk.sent_tokenize(raw_text))

        return sentence_list


docx_extract_svc = DocxSvc()

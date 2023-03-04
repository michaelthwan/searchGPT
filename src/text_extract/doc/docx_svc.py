import docx

from Util import split_sentences_from_paragraph
from text_extract.doc.abc_doc_extract import AbstractDocExtractSvc


class DocxSvc(AbstractDocExtractSvc):
    def __init__(self):
        super().__init__()

    def extract_from_doc(self, path: str):
        doc_file = docx.Document(path)
        raw_text_list = [paragraph.text for paragraph in doc_file.paragraphs if len(paragraph.text) > 0]
        sentence_list = list()
        for raw_text in raw_text_list:
            sentence_list.extend(split_sentences_from_paragraph(raw_text))

        # Remove duplicates
        sentence_list = list(dict.fromkeys(sentence_list))

        return sentence_list


docx_extract_svc = DocxSvc()

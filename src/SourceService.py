import glob
import os

import pandas as pd

from BingService import BingService
from Util import setup_logger
from text_extract.doc import support_doc_type, doc_extract_svc_map
from text_extract.doc.abc_doc_extract import AbstractDocExtractSvc
from website.sender import Sender, MSG_TYPE_SEARCH_STEP

logger = setup_logger('SourceModule')


class SourceService:
    def __init__(self, config, sender: Sender = None):
        self.config = config
        self.sender = sender

    def extract_bing_text_df(self, search_text):
        # BingSearch using search_text
        #   check if bing search result is cached and load if exists
        bing_text_df = None
        if not self.config['source_service']['is_use_source'] or not self.config['source_service']['is_enable_bing_search']:
            return bing_text_df

        bing_service = BingService(self.config)
        if self.sender is not None:
            self.sender.send_message(msg_type=MSG_TYPE_SEARCH_STEP, msg="Calling bing search API")
        website_df = bing_service.call_bing_search_api(search_text=search_text)
        if self.sender is not None:
            self.sender.send_message(msg_type=MSG_TYPE_SEARCH_STEP, msg="Extracting sentences from bing search result ...")
        bing_text_df = bing_service.call_urls_and_extract_sentences_concurrent(website_df=website_df)

        return bing_text_df

    def extract_doc_text_df(self, bing_text_df):
        # DocSearch using doc_search_path
        #  bing_text_df is used for doc_id arrangement
        if not self.config['source_service']['is_use_source'] or not self.config['source_service']['is_enable_doc_search']:
            return pd.DataFrame([])
        if self.sender is not None:
            self.sender.send_message(msg_type=MSG_TYPE_SEARCH_STEP, msg="Extracting sentences from document")
        files_grabbed = list()
        for doc_type in support_doc_type:
            tmp_file_list = glob.glob(self.config['source_service']['doc_search_path'] + os.sep + "*." + doc_type)
            files_grabbed.extend({"file_path": file_path, "doc_type": doc_type} for file_path in tmp_file_list)

        logger.info(f"File list: {files_grabbed}")
        doc_sentence_list = list()

        start_doc_id = 1 if bing_text_df is None else bing_text_df['url_id'].max() + 1
        for doc_id, file in enumerate(files_grabbed, start=start_doc_id):
            extract_svc: AbstractDocExtractSvc = doc_extract_svc_map[file['doc_type']]
            sentence_list = extract_svc.extract_from_doc(file['file_path'])

            file_name = file['file_path'].split(os.sep)[-1]
            for sentence in sentence_list:
                doc_sentence_list.append({
                    'name': file_name,
                    'url': file['file_path'],
                    'url_id': doc_id,
                    'snippet': '',
                    'text': sentence
                })
        doc_text_df = pd.DataFrame(doc_sentence_list)
        return doc_text_df

import glob
import os

import pandas as pd
import yaml

from BingService import BingService
from FootnoteService import FootnoteService
from LLMService import LLMServiceFactory
from PyTerrierService import PyTerrierService
from Util import post_process_gpt_input_text_df, setup_logger
from text_extract.doc import support_doc_type, doc_extract_svc_map
from text_extract.doc.abc_doc_extract import AbstractDocExtractSvc

logger = setup_logger('SearchGPTService')


class SearchGPTService:
    def __init__(self):
        with open('config/config.yaml') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def _prompt(self, search_text, text_df):
        pyterrier_service = PyTerrierService()
        gpt_input_text_df = pyterrier_service.retrieve_search_query_in_dfindexer(search_text, text_df)
        llm_service = LLMServiceFactory.creaet_llm_service(self.config)
        prompt = llm_service.get_prompt(search_text, gpt_input_text_df)
        print('===========Prompt:============')
        print(prompt)
        print('===========Search:============')
        print(search_text)
        gpt_input_text_df = post_process_gpt_input_text_df(gpt_input_text_df, self.config.get('openai_api').get('prompt').get('prompt_length_limit'))
        response_text = llm_service.call_api(prompt)
        print('===========Response text (raw):============')
        print(response_text)
        footnote_service = FootnoteService(self.config, response_text, gpt_input_text_df, pyterrier_service)
        footnote_result_list, in_scope_source_df = footnote_service.get_footnote_from_sentences()
        response_text_with_footnote, source_text = footnote_service.pretty_print_footnote_result_list(footnote_result_list, gpt_input_text_df)
        data_json = footnote_service.extract_data_json(footnote_result_list, gpt_input_text_df)
        return response_text, response_text_with_footnote, source_text, data_json

    def query_and_get_answer(self, search_text):
        bing_text_df, doc_text_df = None, None

        if self.config['search_option']['is_enable_bing_search']:
            bing_service = BingService(self.config)
            website_df = bing_service.call_bing_search_api(search_text)
            bing_text_df = bing_service.call_urls_and_extract_sentences(website_df)

        if self.config['search_option']['is_enable_doc_search']:
            files_grabbed = list()
            for doc_type in support_doc_type:
                tmp_file_list = glob.glob(self.config['search_option']['doc_search_path'] + os.sep + "*." + doc_type)
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

        text_df = pd.concat([bing_text_df, doc_text_df], ignore_index=True)

        return self._prompt(search_text, text_df)

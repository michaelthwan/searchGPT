import glob
import os
from pathlib import Path

import pandas as pd
import yaml

from BingService import BingService
from FrontendService import FrontendService
from LLMService import LLMServiceFactory
from SemanticSearchService import BatchOpenAISemanticSearchService
from Util import setup_logger, post_process_gpt_input_text_df, check_result_cache_exists, load_result_from_cache, save_result_cache, check_max_number_of_cache, get_project_root
from text_extract.doc import support_doc_type, doc_extract_svc_map
from text_extract.doc.abc_doc_extract import AbstractDocExtractSvc

logger = setup_logger('SearchGPTService')


class SearchGPTService:
    def __init__(self, ui_overriden_config=None):
        with open(os.path.join(get_project_root(), 'src/config/config.yaml')) as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        self.overide_config_by_query_string(ui_overriden_config)
        self.validate_config()

    def overide_config_by_query_string(self, ui_overriden_config):
        if ui_overriden_config is None:
            return
        for key, value in ui_overriden_config.items():
            if value is not None and value != '':
                # query_string is flattened (one level) while config.yaml is nested (two+ levels)
                # Any better way to handle this?
                if key == 'bing_search_subscription_key':
                    self.config['bing_search']['subscription_key'] = value
                elif key == 'openai_api_key':
                    self.config['openai_api']['api_key'] = value
                elif key == 'is_use_source':
                    self.config['search_option']['is_use_source'] = False if value.lower() in ['false', '0'] else True
                elif key == 'llm_service_provider':
                    self.config['llm_service']['provider'] = value
                elif key == 'llm_model':
                    if self.config['llm_service']['provider'] == 'openai':
                        self.config['openai_api']['model'] = value
                    elif self.config['llm_service']['provider'] == 'goose_ai':
                        self.config['goose_ai_api']['model'] = value
                    else:
                        raise Exception(f"llm_model is not supported for llm_service_provider: {self.config['llm_service']['provider']}")
                elif key == 'semantic_search_provider':
                    self.config['semantic_search']['provider'] = value
                else:
                    # invalid query_string but not throwing exception first
                    pass

    def validate_config(self):
        if self.config['search_option']['is_enable_bing_search']:
            assert self.config['bing_search']['subscription_key'], 'bing_search_subscription_key is required'
        if self.config['llm_service']['provider'] == 'openai':
            assert self.config['openai_api']['api_key'], 'openai_api_key is required'

    def _prompt(self, search_text, text_df, cache_path=None):
        semantic_search_service = BatchOpenAISemanticSearchService(self.config)
        gpt_input_text_df = semantic_search_service.search_related_source(text_df, search_text)
        gpt_input_text_df = post_process_gpt_input_text_df(gpt_input_text_df, self.config.get('openai_api').get('prompt').get('prompt_length_limit'))

        llm_service_provider = self.config.get('llm_service').get('provider')
        # check if llm result is cached and load if exists
        if self.config.get('cache').get('is_enable_cache') and check_result_cache_exists(cache_path, search_text, llm_service_provider):
            logger.info(f"SemanticSearchService.load_result_from_cache. search_text: {search_text}, cache_path: {cache_path}")
            cache = load_result_from_cache(cache_path, search_text, llm_service_provider)
            prompt, response_text = cache['prompt'], cache['response_text']
        else:
            llm_service = LLMServiceFactory.create_llm_service(self.config)
            prompt = llm_service.get_prompt_v3(search_text, gpt_input_text_df)
            response_text = llm_service.call_api(prompt)

            llm_config = self.config.get(f'{llm_service_provider}_api').copy()
            llm_config.pop('api_key')  # delete api_key to avoid saving it to .cache
            save_result_cache(cache_path, search_text, llm_service_provider, prompt=prompt, response_text=response_text, config=llm_config)

        # check whether the number of cache exceeds the limit
        check_max_number_of_cache(cache_path, self.config.get('cache').get('max_number_of_cache'))

        print('===========Prompt:============')
        print(prompt)
        print('===========Search:============')
        print(search_text)
        print('===========Response text (raw):============')
        print(response_text)

        frontend_service = FrontendService(self.config, response_text, gpt_input_text_df)
        response_text_with_footnote, source_text, data_json = frontend_service.get_data_json(response_text, gpt_input_text_df)

        return response_text, response_text_with_footnote, source_text, data_json

    def _extract_bing_text_df(self, search_text, cache_path):
        # BingSearch using search_text
        #   check if bing search result is cached and load if exists
        bing_text_df = None
        if self.config['search_option']['is_enable_bing_search']:
            if self.config.get('cache').get('is_enable_cache') and check_result_cache_exists(cache_path, search_text, 'bing_search'):
                logger.info(f"BingService.load_result_from_cache. search_text: {search_text}, cache_path: {cache_path}")
                cache = load_result_from_cache(cache_path, search_text, 'bing_search')
                bing_text_df = cache['bing_text_df']
            else:
                bing_service = BingService(self.config)
                website_df = bing_service.call_bing_search_api(search_text)
                bing_text_df = bing_service.call_urls_and_extract_sentences_concurrent(website_df)

                bing_search_config = self.config.get('bing_search').copy()
                bing_search_config.pop('subscription_key')  # delete api_key from config to avoid saving it to .cache
                save_result_cache(cache_path, search_text, 'bing_search', bing_text_df=bing_text_df, config=bing_search_config)
        return bing_text_df

    def _extract_doc_text_df(self, bing_text_df):
        # DocSearch using doc_search_path
        #  bing_text_df is used for doc_id arrangement
        if not self.config['search_option']['is_enable_doc_search']:
            return pd.DataFrame([])
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
        return doc_text_df

    def query_and_get_answer(self, search_text):
        cache_path = Path(self.config.get('cache').get('path'))
        # TODO: strategy pattern to support different text sources (e.g. PDF later)
        bing_text_df = self._extract_bing_text_df(search_text, cache_path)
        doc_text_df = self._extract_doc_text_df(bing_text_df)
        text_df = pd.concat([bing_text_df, doc_text_df], ignore_index=True)

        return self._prompt(search_text, text_df, cache_path)

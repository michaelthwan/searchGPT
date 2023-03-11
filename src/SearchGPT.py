import os
from pathlib import Path

import pandas as pd
import yaml

from FrontendService import FrontendService
from LLMService import LLMServiceFactory
from SemanticSearchService import BatchOpenAISemanticSearchService
from SourceService import SourceService
from Util import setup_logger, check_result_cache_exists, load_result_from_cache, save_result_cache, check_max_number_of_cache, get_project_root

logger = setup_logger('SearchGPTService')


class SearchGPT:
    """
    SearchGPT app->service->child-service structure
    - (Try to) app import service, child-service inherit service

    SearchGPT class
    - SourceService
    -- BingService
    -- Doc/PPT/PDF Service
    - SemanticSearchModule
    - LLMService
    -- OpenAIService
    -- GooseAPIService
    -- FrontendService

    """

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
                    self.config['llm_service']['openai_api']['api_key'] = value
                elif key == 'is_use_source':
                    self.config['search_option']['is_use_source'] = False if value.lower() in ['false', '0'] else True
                elif key == 'llm_service_provider':
                    self.config['llm_service']['provider'] = value
                elif key == 'llm_model':
                    if self.config['llm_service']['provider'] == 'openai':
                        self.config['llm_service']['openai_api']['model'] = value
                    elif self.config['llm_service']['provider'] == 'goose_ai':
                        self.config['llm_service']['goose_ai_api']['model'] = value
                    else:
                        raise Exception(f"llm_model is not supported for llm_service_provider: {self.config['llm_service']['provider']}")
                else:
                    # invalid query_string but not throwing exception first
                    pass

    def validate_config(self):
        if self.config['search_option']['is_enable_bing_search']:
            assert self.config['bing_search']['subscription_key'], 'bing_search_subscription_key is required'
        if self.config['llm_service']['provider'] == 'openai':
            assert self.config['llm_service']['openai_api']['api_key'], 'openai_api_key is required'

    def query_and_get_answer(self, search_text):
        cache_path = Path(self.config.get('cache').get('path')) # TODO: hide cache logic in main entrance

        source_module = SourceService(self.config)
        bing_text_df = source_module.extract_bing_text_df(search_text, cache_path)
        doc_text_df = source_module.extract_doc_text_df(bing_text_df)
        text_df = pd.concat([bing_text_df, doc_text_df], ignore_index=True)


        semantic_search_service = BatchOpenAISemanticSearchService(self.config)
        gpt_input_text_df = semantic_search_service.search_related_source(text_df, search_text)
        gpt_input_text_df = BatchOpenAISemanticSearchService.post_process_gpt_input_text_df(gpt_input_text_df, self.config.get('llm_service').get('openai_api').get('prompt').get('prompt_length_limit'))

        llm_service_provider = self.config.get('llm_service').get('provider')
        # check if llm result is cached and load if exists
        if self.config.get('cache').get('is_enable_cache') and check_result_cache_exists(cache_path, search_text, llm_service_provider):
            # TODO: hide cache logic in main entrance
            logger.info(f"SemanticSearchService.load_result_from_cache. search_text: {search_text}, cache_path: {cache_path}")
            cache = load_result_from_cache(cache_path, search_text, llm_service_provider)
            prompt, response_text = cache['prompt'], cache['response_text']
        else:
            llm_service = LLMServiceFactory.create_llm_service(self.config)
            prompt = llm_service.get_prompt_v3(search_text, gpt_input_text_df)
            response_text = llm_service.call_api(prompt)

            # TODO: hide cache logic in main entrance
            llm_config = self.config.get('llm_service').get(f'{llm_service_provider}_api').copy()
            llm_config.pop('api_key')  # delete api_key to avoid saving it to .cache
            save_result_cache(cache_path, search_text, llm_service_provider, prompt=prompt, response_text=response_text, config=llm_config)

        # TODO: hide cache logic in main entrance
        # check whether the number of cache exceeds the limit
        check_max_number_of_cache(cache_path, self.config.get('cache').get('max_number_of_cache'))

        frontend_service = FrontendService(self.config, response_text, gpt_input_text_df)
        source_text, data_json = frontend_service.get_data_json(response_text, gpt_input_text_df)

        print('===========Prompt:============')
        print(prompt)
        print('===========Search:============')
        print(search_text)
        print('===========Response text:============')
        print(response_text)
        print('===========Source text:============')
        print(source_text)

        return response_text, source_text, data_json

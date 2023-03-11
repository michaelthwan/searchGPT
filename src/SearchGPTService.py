import os

import pandas as pd
import yaml

from FrontendService import FrontendService
from LLMService import LLMServiceFactory
from SemanticSearchService import BatchOpenAISemanticSearchService
from SourceService import SourceService
from Util import setup_logger, get_project_root, storage_cached

logger = setup_logger('SearchGPTService')


class SearchGPTService:
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
    - FrontendService

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
                    self.config['source_service']['bing_search']['subscription_key'] = value
                elif key == 'openai_api_key':
                    self.config['llm_service']['openai_api']['api_key'] = value
                elif key == 'is_use_source':
                    self.config['source_service']['is_use_source'] = False if value.lower() in ['false', '0'] else True
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
        if self.config['source_service']['is_enable_bing_search']:
            assert self.config['source_service']['bing_search']['subscription_key'], 'bing_search_subscription_key is required'
        if self.config['llm_service']['provider'] == 'openai':
            assert self.config['llm_service']['openai_api']['api_key'], 'openai_api_key is required'

    @storage_cached('web', 'search_text')
    def query_and_get_answer(self, search_text):
        source_module = SourceService(self.config)
        bing_text_df = source_module.extract_bing_text_df(search_text)
        doc_text_df = source_module.extract_doc_text_df(bing_text_df)
        text_df = pd.concat([bing_text_df, doc_text_df], ignore_index=True)

        semantic_search_service = BatchOpenAISemanticSearchService(self.config)
        gpt_input_text_df = semantic_search_service.search_related_source(text_df, search_text)
        gpt_input_text_df = BatchOpenAISemanticSearchService.post_process_gpt_input_text_df(gpt_input_text_df,
                                                                                            self.config.get('llm_service').get('openai_api').get('prompt').get('prompt_length_limit'))

        llm_service = LLMServiceFactory.create_llm_service(self.config)
        prompt = llm_service.get_prompt_v3(search_text, gpt_input_text_df)
        response_text = llm_service.call_api(prompt=prompt)

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

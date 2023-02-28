from pathlib import Path

import yaml

from BingService import BingService
from FootnoteService import FootnoteService
from LLMService import LLMServiceFactory
from PyTerrierService import PyTerrierService
from Util import post_process_gpt_input_text_df, check_result_cache_exists, load_result_from_cache, save_result_cache, check_max_number_of_cache


class SearchGPTService:
    def __init__(self):
        with open('config/config.yaml') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def query_and_get_answer(self, search_text):

        cache_path = Path(self.config.get('cache').get('path'))
        # check if bing search result is cached and load if exists
        if self.config.get('cache').get('is_enable_cache') and check_result_cache_exists(cache_path, search_text, 'bing_search'):
            cache = load_result_from_cache(cache_path, search_text, 'bing_search')
            text_df = cache['text_df']
        else:
            bing_service = BingService(self.config)
            website_df = bing_service.call_bing_search_api(search_text)
            text_df = bing_service.call_urls_and_extract_sentences(website_df)

            bing_search_config = self.config.get('bing_search')
            bing_search_config.pop('subscription_key')  # delete api_key from config to avoid saving it to .cache
            save_result_cache(cache_path, search_text, 'bing_search', text_df=text_df, config=bing_search_config)

        # process bing search result for gpt input
        pyterrier_service = PyTerrierService()
        gpt_input_text_df = pyterrier_service.retrieve_search_query_in_dfindexer(search_text, text_df)
        gpt_input_text_df = post_process_gpt_input_text_df(gpt_input_text_df, self.config.get('openai_api').get('prompt').get('prompt_length_limit'))

        llm_service_provider = self.config.get('llm_service').get('provider')
        # check if llm result is cached and load if exists
        if self.config.get('cache').get('is_enable_cache') and check_result_cache_exists(cache_path, search_text, llm_service_provider):
            cache = load_result_from_cache(cache_path, search_text, llm_service_provider)
            prompt, response_text = cache['prompt'], cache['response_text']
        else:
            llm_service = LLMServiceFactory.create_llm_service(self.config)
            prompt = llm_service.get_prompt(search_text, gpt_input_text_df)
            response_text = llm_service.call_api(prompt)

            llm_config = self.config.get(f'{llm_service_provider}_api')
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

        footnote_service = FootnoteService(self.config, response_text, gpt_input_text_df, pyterrier_service)
        footnote_result_list, in_scope_source_df = footnote_service.get_footnote_from_sentences()
        response_text_with_footnote, source_text = footnote_service.pretty_print_footnote_result_list(footnote_result_list, gpt_input_text_df)
        data_json = footnote_service.extract_data_json(footnote_result_list, gpt_input_text_df)

        return response_text, response_text_with_footnote, source_text, data_json

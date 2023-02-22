import yaml

from BingService import BingService
from PyTerrierService import PyTerrierService
from LLMService import LLMServiceFactory
from FootnoteService import FootnoteService

from Util import post_process_gpt_input_text_df


class SearchGPTService:
    def __init__(self):
        with open('config/config.yaml') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def query_and_get_answer(self, search_text):
        bing_service = BingService(self.config)
        website_df = bing_service.call_bing_search_api(search_text)
        text_df = bing_service.call_urls_and_extract_sentences(website_df)

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
        return response_text, response_text_with_footnote, source_text

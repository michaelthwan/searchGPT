import yaml

from BingService import BingService
from PyTerrierService import PyTerrierService
from LLMService import LLMServiceFactory, LLMService

from Util import pretty_print_source

if __name__ == '__main__':
    search_text = 'the source of dark energy'

    # Load config
    with open('config/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        bing_service = BingService(config)
        website_df = bing_service.call_bing_search_api(search_text)
        text_df = bing_service.call_urls_and_extract_sentences(website_df)

        pyterrier_service = PyTerrierService()
        gpt_input_text_df = pyterrier_service.retrieve_search_query_in_dfindexer(search_text, text_df)
        llm_service = LLMServiceFactory().creaet_llm_service(config)
        prompt = llm_service.get_prompt(search_text, gpt_input_text_df)
        print('===========Prompt:============')
        print(prompt)
        print('===========Search:============')
        print(search_text)
        print('===========Ground sources:============')
        pretty_print_source(gpt_input_text_df, config.get('openai_api').get('prompt').get('prompt_length_limit'))
        response_text = llm_service.call_api(prompt)
        print('===========Response text:============')
        print(response_text)

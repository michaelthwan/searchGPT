import yaml

from BingService import BingService
from PyTerrierService import PyTerrierService
from OpenAIService import OpenAIService

if __name__ == '__main__':
    search_text = 'How to train a dog'

    # Load config
    with open('config/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        bing_service = BingService(config)
        website_df = bing_service.call_bing_search_api(search_text)
        text_df = bing_service.call_urls_and_extract_sentences(website_df)

        pyterrier_service = PyTerrierService()
        gpt_input_text_df = pyterrier_service.retrieve_search_query_in_dfindexer(search_text, text_df)
        print(gpt_input_text_df)

        openai_service = OpenAIService(config)
        prompt = openai_service.get_prompt(search_text, gpt_input_text_df)
        print('===========Search:============')
        print(search_text)
        print('===========Prompt:============')
        print(prompt)
        response_text = openai_service.call_openai_api(prompt)
        print('===========Response text:============')
        print(response_text)

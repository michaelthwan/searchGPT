import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup
from pprint import pprint

'''
This sample makes a call to the Bing Web Search API with a query and returns relevant web search.
Documentation: https://docs.microsoft.com/en-us/bing/search-apis/bing-web-search/overview
'''


class BingService:
    def __init__(self, config):
        self.config = config

    def call_bing_search_api(self, query: str):
        # Add your Bing Search V7 subscription key and endpoint to your environment variables.
        subscription_key = self.config.get('bing_search').get('subscription_key')
        endpoint = self.config.get('bing_search').get('end_point') + "/v7.0/search"
        # Construct a request
        mkt = 'en-US'
        params = {'q': query, 'mkt': mkt}
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}

        # Call the API
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()

            # print("Headers:")
            # print(response.headers)

            # print("JSON Response:")
            # pprint(response.json())
            columns = ['name', 'url', 'snippet']
            website_df = pd.DataFrame(response.json()['webPages']['value'])[columns]
            website_df = website_df[:self.config.get('bing_search').get('result_count')]
        except Exception as ex:
            raise ex
        return website_df

    def call_urls_and_extract_sentences(self, website_df):
        name_list, url_list, snippet_list, text_list = [], [], [], []
        for index, row in website_df.iterrows():
            sentences = self.extract_sentences_from_url(row['url'])
            for text in sentences:
                name_list.append(row['name'])
                url_list.append(row['url'])
                snippet_list.append(row['snippet'])
                text_list.append(text)
        text_df = pd.DataFrame(data=zip(name_list, url_list, snippet_list, text_list), columns=['name', 'url', 'snippet', 'text'])
        return text_df

    def extract_sentences_from_url(self, url):
        # Fetch the HTML content of the page
        response = requests.get(url)
        html_content = response.text

        # Use BeautifulSoup to parse the HTML and extract the text
        soup = BeautifulSoup(html_content, "html.parser")
        p = [el.get_text() for el in soup.select('p')]  # How about h1/h2/h3 etc?
        return p


if __name__ == '__main__':
    # Load config
    with open('config/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        service = BingService(config)
        website_df = service.call_bing_search_api('What is ChatGPT')
        text_df = service.call_urls_and_extract_sentences(website_df)
        print(text_df)

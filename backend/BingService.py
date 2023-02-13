from pprint import pprint

import pandas as pd
import requests
import yaml

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
            df = pd.DataFrame(response.json()['webPages']['value'])[columns]
        except Exception as ex:
            raise ex
        return df


if __name__ == '__main__':
    # Load config
    with open('config/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        service = BingService(config)
        df = service.call_bing_search_api('What is ChatGPT')
        print(df)

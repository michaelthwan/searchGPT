import pandas as pd
import requests
import yaml

from Util import setup_logger
from backend.src.text_extract.beautiful_soup import BeautifulSoupSvc
from backend.src.text_extract.trafilatura import TrafilaturaSvc

logger = setup_logger('BingService')


class BingService:
    def __init__(self, config):
        self.config = config
        extract_svc = self.config.get('bing_search').get('text_extract')
        if extract_svc == 'trafilatura':
            self.txt_extract_svc = TrafilaturaSvc()
        elif extract_svc == 'beautifulsoup':
            self.txt_extract_svc = BeautifulSoupSvc()

    def call_bing_search_api(self, query: str) -> pd.DataFrame:
        logger.info("BingService.call_bing_search_api. query: " + query)
        subscription_key = self.config.get('bing_search').get('subscription_key')
        endpoint = self.config.get('bing_search').get('end_point') + "/v7.0/search"
        mkt = 'en-US'
        params = {'q': query, 'mkt': mkt}
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}

        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()

            columns = ['name', 'url', 'snippet']
            website_df = pd.DataFrame(response.json()['webPages']['value'])[columns]
            website_df['url_id'] = website_df.index + 1
            website_df = website_df[:self.config.get('bing_search').get('result_count')]
        except Exception as ex:
            raise ex
        return website_df

    def call_urls_and_extract_sentences(self, website_df) -> pd.DataFrame:
        """
        :param:
            website_df: one row = one website with url
                name: website title name
                url: url
                snippet: snippet of the website given by BingAPI
        :return:
            text_df: one row = one website sentence
            columns:
                name: website title name
                url: url
                snippet: snippet of the website given by BingAPI
                text: setences extracted from the website
        """
        logger.info(f"BingService.call_urls_and_extract_sentences. website_df.shape: {website_df.shape}")
        name_list, url_list, url_id_list, snippet_list, text_list = [], [], [], [], []
        for index, row in website_df.iterrows():
            logger.info(f"Processing url: {row['url']}")
            sentences = self.extract_sentences_from_url(row['url'])
            for text in sentences:
                if len(text) < 10:
                    continue
                name_list.append(row['name'])
                url_list.append(row['url'])
                url_id_list.append(row['url_id'])
                snippet_list.append(row['snippet'])
                text_list.append(text)
        text_df = pd.DataFrame(data=zip(name_list, url_list, url_id_list, snippet_list, text_list),
                               columns=['name', 'url', 'url_id', 'snippet', 'text'])
        return text_df

    def extract_sentences_from_url(self, url):
        # Fetch the HTML content of the page
        try:
            response = requests.get(url, timeout=3)
        except:
            logger.error(f"Failed to fetch url: {url}")
            return []
        html_content = response.text

        # Use BeautifulSoup to parse the HTML and extract the text
        extract_text = self.txt_extract_svc.extract_from_html(html_content)
        return extract_text


if __name__ == '__main__':
    # Load config
    with open('config/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        service = BingService(config)
        website_df = service.call_bing_search_api('What is ChatGPT')
        print("===========Website df:============")
        print(website_df)
        text_df = service.call_urls_and_extract_sentences(website_df)
        print("===========text df:============")
        print(text_df)

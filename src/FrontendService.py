import re
from urllib.parse import urlparse

from SemanticSearchService import BatchOpenAISemanticSearchService
from Util import setup_logger

logger = setup_logger('FootnoteService')


class FrontendService:
    def __init__(self, config, response_text, gpt_input_text_df):
        self.config = config
        self.response_text = response_text
        used_columns = ['docno', 'name', 'url', 'url_id', 'text', 'len_text', 'in_scope']  # TODO: add url_id
        self.gpt_input_text_df = gpt_input_text_df[used_columns]

    def get_data_json(self, response_text, gpt_input_text_df):
        def create_response_json_object(text, type):
            return {"text": text, "type": type}

        def create_source_json_object(footnote, domain, url, title, text):
            return {"footnote": footnote, "domain": domain, "url": url, "title": title, "text": text}

        def get_response_json(response_text):
            response_json = []
            split_sentence = re.findall(r'\[[0-9]+\]|[^\[\]]+', response_text)
            for sentence in split_sentence:
                if sentence.startswith('[') and sentence.endswith(']'):
                    response_json.append(create_response_json_object(sentence, "footnote"))
                else:
                    response_json.append(create_response_json_object(sentence, "response"))
            return response_json

        def get_source_json(gpt_input_text_df):
            in_scope_source_df = gpt_input_text_df[gpt_input_text_df['in_scope']].copy()
            in_scope_source_df.loc[:, 'docno'] = in_scope_source_df['docno'].astype(int)
            in_scope_source_df.sort_values('docno', inplace=True)
            source_text_list = []
            source_json = []
            source_url_df = in_scope_source_df[['url_id', 'url', 'name', 'snippet']].drop_duplicates().sort_values('url_id').reset_index(drop=True)
            for index, row in source_url_df.iterrows():
                url_text = ''
                url_text += f"[{row['url_id']}] {row['url']}\n"

                for index, row in in_scope_source_df[in_scope_source_df['url_id'] == row['url_id']].iterrows():
                    url_text += f"  {row['text']}\n"

                source_text_list.append(url_text)

                domain_name = urlparse(row['url']).netloc.replace('www.', '')
                source_json.append(create_source_json_object(f"[{row['url_id']}]", domain_name, row['url'], row['name'], row['snippet']))
            source_text = ''.join(sorted(source_text_list))

            source_json = sorted(source_json, key=lambda x: x['footnote'])
            return source_json, source_text

        response_json = get_response_json(response_text)
        source_json, source_text = get_source_json(gpt_input_text_df)

        return source_text, {'response_json': response_json, 'source_json': source_json}


if __name__ == '__main__':
    sentence = "According to the sources [1] [2], it is predicted that the world's natural gas reserves will last about 52.8 years with the current rate of production. [13] TestTest."
    split_sentence = re.findall(r'\[[0-9]+\]|[^\[\]]+', sentence)
    print(split_sentence)

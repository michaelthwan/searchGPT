from urllib.parse import urlparse

import nltk
import pandas as pd
import pyterrier as pt

from SemanticSearchService import SemanticSearchService
from Util import setup_logger

logger = setup_logger('FootnoteService')


class FootnoteService:
    def __init__(self, config, response_text, gpt_input_text_df, semantic_search_service: SemanticSearchService):
        self.config = config
        self.response_text = response_text
        used_columns = ['docno', 'name', 'url', 'url_id', 'text', 'len_text', 'in_scope']  # TODO: add url_id
        self.gpt_input_text_df = gpt_input_text_df[used_columns]
        self.semantic_search_service = semantic_search_service

        if self.config.get('semantic_search').get('provider') == 'pyterrier':
            if not pt.started():
                pt.init()

    def extract_sentences_from_paragraph(self):
        # TODO: currently only support English
        sentences = nltk.sent_tokenize(self.response_text)
        response_df = pd.DataFrame(sentences, columns=['response_text_sentence'])
        return response_df

    def get_footnote_from_sentences(self):
        logger.info(f'FootnoteService.get_footnote_from_sentences()')
        response_sentences_df = self.extract_sentences_from_paragraph()
        in_scope_source_df = self.gpt_input_text_df[self.gpt_input_text_df['in_scope']]
        source_index = self.semantic_search_service.index_text_df(in_scope_source_df, 'source_index')

        footnote_result_list = []
        for index, row in response_sentences_df.iterrows():
            response_text_sentence = row["response_text_sentence"]
            logger.info(f'  [S{index + 1}] {response_text_sentence}')
            # print(f'[S{index + 1}] {response_text_sentence}')

            cleaned_response_text_sentence = self.semantic_search_service.clean_sentence_to_avoid_lexical_error(response_text_sentence)
            result_df = self.semantic_search_service.use_index_to_search(source_index, cleaned_response_text_sentence)
            result_df = result_df.merge(in_scope_source_df, on="docno", how="left")[['docno', 'rank', 'score', 'url', 'url_id', 'text']]

            if self.semantic_search_service.provider == 'pyterrier':
                SCORE_THRESHOLD = 5
                result_within_scope_df = result_df[result_df['score'] >= SCORE_THRESHOLD]
            elif self.semantic_search_service.provider in ['faiss-openai', 'faiss-huggingface']:
                # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
                # print(f'sentence {index}')
                # print(result_df[['text', 'url_id', 'score']])
                SCORE_THRESHOLD = 0.6
                top_k = 1
                # # distance for faiss (lower is closer)
                # result_within_scope_df = result_df[result_df['score'] <= SCORE_THRESHOLD].head(top_k)
                result_within_scope_df = result_df.head(top_k)
            else:
                NotImplementedError(f'Unsupported semantic search provider: {self.semantic_search_service.provider}')

            footnote_result_sentence_dict = {
                'sentence': response_text_sentence,
                'docno': result_within_scope_df['docno'].tolist(),
                'rank': result_within_scope_df['rank'].tolist(),
                'score': result_within_scope_df['score'].tolist(),
                'url_unique_ids': sorted(result_within_scope_df['url_id'].unique().tolist()),
                'url': result_within_scope_df['url'].tolist(),
                'url_ids': result_within_scope_df['url_id'].tolist(),
                'source_sentence': result_within_scope_df['text'].tolist()
            }
            footnote_result_list.append(footnote_result_sentence_dict)
        return footnote_result_list, in_scope_source_df

    def pretty_print_footnote_result_list(self, footnote_result_list, gpt_input_text_df):
        def create_response_json_object(text, type):
            return {"text": text, "type": type}

        def create_source_json_object(footnote, domain, url, title, text):
            return {"footnote": footnote, "domain": domain, "url": url, "title": title, "text": text}

        url_id_map = {}  # to reassign url_id as per appearance order

        # footnote text and json processing
        response_text_with_footnote = ''
        response_json = []

        for footnote_result in footnote_result_list:
            footnote_print = []
            response_json.append(create_response_json_object(footnote_result["sentence"], "response"))

            for url_id in footnote_result['url_unique_ids']:

                if url_id not in url_id_map:
                    url_id_map[url_id] = len(url_id_map) + 1

                footnote_print += [f'[{url_id_map[url_id]}]']
                response_json.append(create_response_json_object(f'[{url_id_map[url_id]}]', "footnote"))

            response_text_with_footnote += f'{footnote_result["sentence"]}{" " + "".join(sorted(footnote_print)) if len(footnote_print) > 0 else ""} '

        # source text and json processing
        in_scope_source_df = gpt_input_text_df[gpt_input_text_df['in_scope']].copy()
        in_scope_source_df.loc[:, 'docno'] = in_scope_source_df['docno'].astype(int)
        in_scope_source_df.sort_values('docno', inplace=True)

        source_text_list = []
        source_json = []

        source_url_df = in_scope_source_df[['url_id', 'url', 'name', 'snippet']].drop_duplicates().sort_values('url_id').reset_index(drop=True)
        for index, row in source_url_df.iterrows():
            if row['url_id'] not in url_id_map:
                continue

            url_text = ''
            url_text += f"[{url_id_map[row['url_id']]}] {row['url']}\n"

            for index, row in in_scope_source_df[in_scope_source_df['url_id'] == row['url_id']].iterrows():
                url_text += f"  {row['text']}\n"

            source_text_list.append(url_text)

            domain_name = urlparse(row['url']).netloc.replace('www.', '')
            source_json.append(create_source_json_object(f"[{url_id_map[row['url_id']]}]", domain_name, row['url'], row['name'],row['snippet']))

        source_text = ''.join(sorted(source_text_list))
        source_json = sorted(source_json, key=lambda x: x['footnote'])

        print('===========Response text (ref):============')
        print(response_text_with_footnote)
        print()
        print('===========Source text:============')
        print(source_text)
        print()

        return response_text_with_footnote, source_text, {'response_json': response_json, 'source_json': source_json}

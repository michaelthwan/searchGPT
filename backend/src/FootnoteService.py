import nltk
import pandas as pd
import pyterrier as pt
from urllib.parse import urlparse

from PyTerrierService import PyTerrierService


class FootnoteService:
    def __init__(self, config, response_text, gpt_input_text_df, pyterrier_service: PyTerrierService):
        self.config = config
        self.response_text = response_text
        used_columns = ['docno', 'name', 'url', 'url_id', 'text', 'len_text', 'is_used']  # TODO: add url_id
        self.gpt_input_text_df = gpt_input_text_df[used_columns]
        self.pyterrier_service = pyterrier_service

        if not pt.started():
            pt.init()

    def extract_sentences_from_paragraph(self):
        # TODO: currently only support English
        sentences = nltk.sent_tokenize(self.response_text)
        response_df = pd.DataFrame(sentences, columns=['response_text_sentence'])
        return response_df

    def get_footnote_from_sentences(self):
        response_sentences_df = self.extract_sentences_from_paragraph()
        in_scope_source_df = self.gpt_input_text_df[self.gpt_input_text_df['is_used']]
        source_indexref = self.pyterrier_service.index_text_df(in_scope_source_df, 'source_index')

        footnote_result_list = []
        for index, row in response_sentences_df.iterrows():
            response_text_sentence = row["response_text_sentence"]
            # print(f'[S{index + 1}] {response_text_sentence}')

            cleaned_response_text_sentence = self.pyterrier_service.clean_sentence_to_avoid_lexical_error(response_text_sentence)
            result_df = pt.BatchRetrieve(source_indexref).search(cleaned_response_text_sentence)
            result_df = result_df.merge(in_scope_source_df, on="docno", how="left")[['docno', 'rank', 'score', 'url', 'url_id', 'text']]

            SCORE_THRESHOLD = 5
            result_within_scope_df = result_df[result_df['score'] >= SCORE_THRESHOLD]

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
        print('===========Response text (ref):============')
        response_text_with_footnote = ''
        for footnote_result in footnote_result_list:
            footnote_print = ''
            for url_id in footnote_result['url_unique_ids']:
                footnote_print += f'[{url_id}]'
            sentence_with_footnote = f'{footnote_result["sentence"]} {footnote_print}'
            print(sentence_with_footnote)
            response_text_with_footnote += sentence_with_footnote + ' '

        print('===========Source text:============')
        in_scope_source_df = gpt_input_text_df[gpt_input_text_df['is_used']]
        in_scope_source_df['docno'] = in_scope_source_df['docno'].astype(int)
        in_scope_source_df.sort_values('docno', inplace=True)

        source_url_df = in_scope_source_df[['url_id', 'url']].drop_duplicates().sort_values('url_id').reset_index(drop=True)
        # for list with index

        source_text = ""
        for index, row in source_url_df.iterrows():
            print('---------------------')
            source_text += f"[{row['url_id']}] {row['url']}\n"
            # print(f"[{row['url_id']}] {row['url']}")
            for index, row in in_scope_source_df[in_scope_source_df['url_id'] == row['url_id']].iterrows():
                source_text += f"  {row['text']}\n"
                # print(f'  {row["text"]}')
        print(source_text)
        print()
        print('===========footnote_result_list:============')
        print(footnote_result_list)
        return response_text_with_footnote, source_text

    def extract_data_json(self, footnote_result_list, gpt_input_text_df):
        def create_response_json_object(text, type):
            return {"text": text, "type": type}

        def create_source_json_object(footnote, domain, url, title, text):
            return {"footnote": footnote, "domain": domain, "url": url, "title": title, "text": text}

        response_json = []
        for footnote_result in footnote_result_list:
            response_json.append(
                create_response_json_object(footnote_result["sentence"], "response")
            )
            for url_id in footnote_result['url_unique_ids']:
                response_json.append(
                    create_response_json_object(f'[{url_id}]', "footnote")
                )

        in_scope_source_df = gpt_input_text_df[gpt_input_text_df['is_used']]
        in_scope_source_df['docno'] = in_scope_source_df['docno'].astype(int)
        in_scope_source_df.sort_values('docno', inplace=True)

        source_url_df = in_scope_source_df[['url_id', 'url', 'name', 'snippet']].drop_duplicates().sort_values('url_id').reset_index(drop=True)
        # for list with index
        source_json = []
        for index, row in source_url_df.iterrows():
            # source_text += f"[{row['url_id']}] {row['url']}\n"
            # for index, row in in_scope_source_df[in_scope_source_df['url_id'] == row['url_id']].iterrows():
            #     source_text += f"  {row['text']}\n"
            domain_name = urlparse(row['url']).netloc.replace('www.', '')
            source_json.append(
                create_source_json_object(f"[{row['url_id']}]", domain_name, row['url'], row['name'], row['snippet'])
            )
        return {'response_json': response_json, 'source_json': source_json}

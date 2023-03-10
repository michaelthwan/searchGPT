import re
from urllib.parse import urlparse

from Util import setup_logger
from NLPUtil import split_with_delimiters, get_longest_common_word_sequences

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

        def reorder_url_id(response_text, gpt_input_text_df):
            # response_text: find reference in text & re-order
            url_id_list = [int(x) for x in dict.fromkeys(re.findall(r'\[([0-9]+)\]', response_text))]
            url_id_map = dict(zip(url_id_list, range(1, len(url_id_list) + 1)))

            for url_id, new_url_id in url_id_map.items():
                response_text = response_text.replace(f'[{url_id}]', f'[{new_url_id}]')

            # gpt_input_text_df: find reference in text & re-order
            in_scope_source_df = gpt_input_text_df[gpt_input_text_df['url_id'].isin(url_id_map.keys()) & gpt_input_text_df['in_scope']].copy()
            in_scope_source_df['url_id'] = in_scope_source_df['url_id'].map(url_id_map)
            return response_text, in_scope_source_df

        def get_response_json(response_text):
            response_json = []
            split_sentence = re.findall(r'\[[0-9]+\]|[^\[\]]+', response_text)

            for sentence in split_sentence:
                if sentence.startswith('[') and sentence.endswith(']'):
                    response_json.append(create_response_json_object(sentence, "footnote"))
                else:
                    response_json.append(create_response_json_object(sentence, "response"))
            return response_json

        def get_source_json(in_scope_source_df):
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

        def get_explainability_json(response_text, source_text):
            def get_colors():
                return ['#ffe3e8', '#f1e1ff', '#c5d5ff', '#c5efff', '#d6fffa', '#e7ffe7', '#f7ffa7', '#fff3b3', '#ffdfdf', '#ffcaca']

            def create_response_json_object(text, type, color):
                return {"text": text, "type": type, "color": color}

            def get_explain_json(text, word_color_dict):
                common_word_sequences = list(word_color_dict.keys())
                word_list = split_with_delimiters(text.lower(), common_word_sequences + ['\n'])
                explain_json = []
                for word in word_list:
                    if word == '\n':
                        explain_json.append(create_response_json_object(word, "newline", ""))
                    elif word.lower() in common_word_sequences:
                        explain_json.append(create_response_json_object(word, "keyword", word_color_dict[word.lower()]))
                    else:
                        explain_json.append(create_response_json_object(word, "word", ""))
                return explain_json

            longest_common_word_sequences = get_longest_common_word_sequences(response_text, source_text, k=10)
            word_color_dict = {longest_common_word_sequences[i]: get_colors()[i] for i in range(min(len(longest_common_word_sequences), len(get_colors())))}

            response_explain_json = get_explain_json(response_text, word_color_dict)
            source_explain_json = get_explain_json(source_text, word_color_dict)
            return response_explain_json, source_explain_json

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

        response_text, in_scope_source_df = reorder_url_id(response_text, gpt_input_text_df)
        response_json = get_response_json(response_text)
        source_json, source_text = get_source_json(in_scope_source_df)
        response_explain_json, source_explain_json = get_explainability_json(response_text, source_text)

        return source_text, {'response_json': response_json,
                             'source_json': source_json,
                             'response_explain_json': response_explain_json,
                             'source_explain_json': source_explain_json
                             }


if __name__ == '__main__':
    paragraph1 = "ChatGPT is an AI chatbot that can understand and generate human-like answers to text prompts, as well as create code from natural speech [3]. It is built on a family of large language models collectively called GPT-3, which is trained on huge amounts of data [3][1]. The model is fine-tuned from a model in the GPT-3.5 series, which finished training in early 2022 and trained on an Azure AI supercomputing infrastructure [1]. ChatGPT is also sensitive to tweaks to the input phrasing or attempting the same prompt multiple times [1]. The objective of ChatGPT is to predict the next word in a sentence based on what it has learned [3]. The research release of ChatGPT in November 2022 is among OpenAI's iterative deployment of increasingly safe and useful AI systems [1]. ChatGPT Plus also exists, which brings a few benefits over the free tier [3]."
    paragraph2 = """
Source (1)
ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response.
- ChatGPT is sensitive to tweaks to the input phrasing or attempting the same prompt multiple times. For example, given one phrasing of a question, the model can claim to not know the answer, but given a slight rephrase, can answer correctly.
ChatGPT is fine-tuned from a model in the GPT-3.5 series, which finished training in early 2022. You can learn more about the 3.5 series here. ChatGPT and GPT-3.5 were trained on an Azure AI supercomputing infrastructure.
Todayâs research release of ChatGPT is the latest step in OpenAI iterative deployment of increasingly safe and useful AI systems. Many lessons from deployment of earlier models like GPT-3 and Codex have informed the safety mitigations in place for this release, including substantial reductions in harmful and untruthful outputs achieved by the use of reinforcement learning from human feedback (RLHF).

Source (3)
ChatGPT is an AI chatbot that's built on a family of large language models (LLMs) that are collectively called GPT-3. These models can understand and generate human-like answers to text prompts, because they've been trained on huge amounts of data.
But ChatGPT is also equally talented at coding and productivity tasks. For the former, its ability to create code from natural speech makes it a powerful ally for both new and experienced coders who either aren't familiar with a particular language or want to troubleshoot existing code. Unfortunately, there is also the potential for it to be misused to create malicious emails and malware.
ChatGPT stands for "Chat Generative Pre-trained Transformer". Let's take a look at each of those words in turn.
But the short answer? ChatGPT works thanks to a combination of deep learning algorithms, a dash of natural language processing, and a generous dollop of generative pre-training, which all combine to help it produce disarmingly human-like responses to text questions. Even if all it's ultimately been trained to do is fill in the next word, based on its experience of being the world's most voracious reader.
ChatGPT has been created with one main objective to predict the next word in a sentence, based on what's typically happened in the gigabytes of text data that it's been trained on.
ChatGPT was released as a "research preview" on November 30, 2022. A blog post (opens in new tab) casually introduced the AI chatbot to the world, with OpenAI stating that "we’ve trained a model called ChatGPT which interacts in a conversational way".
ChatGPT Plus costs $20 p/month (around £17 / AU$30) and brings a few benefits over the free tier. It promises to give you full access to ChatGPT even during peak times, which is when you'll otherwise frequently see "ChatGPT is at capacity right now messages during down times.
ChatGPT has been trained on a vast amount of text covering a huge range of subjects, so its poss
    """

    # common_stems = FrontendService.longest_common_word_sequences(paragraph1, paragraph2)
    # # print(common_stems)
    # for common_stem in common_stems:
    #     print(common_stem)

    # text_list = ["is fine-tuned from a model in the gpt-3.5 series, which finished training in early",
    #              "sensitive to tweaks to the input phrasing or attempting the same prompt multiple",
    #              "is fine-tuned from a model in the gpt-3.5 series, which finished training in",
    #              "is fine-tuned from a model in the gpt-3.5 series, which finished training",
    #              "sensitive to tweaks to the input phrasing or attempting the same prompt",
    #              "is fine-tuned from a model in the gpt-3.5 series, which finished",
    #              "sensitive to tweaks to the input phrasing or attempting the same",
    #              "sensitive to tweaks to the input phrasing or attempting the",
    #              "is fine-tuned from a model in the gpt-3.5 series, which"]
    # text_list = FrontendService.remove_substrings(text_list)
    # for text in text_list:
    #     print(text)

    response_text = "is fine-tuned from a gpt-3.5 series"
    split_list = FrontendService.split_with_delimiters(response_text, ["fine-tuned", "gpt-3.5"])
    for sentence in split_list:
        print(sentence)

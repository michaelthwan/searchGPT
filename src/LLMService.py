import os
from abc import ABC, abstractmethod
from urllib.parse import urlparse

import openai
import pandas as pd
import yaml

from Util import setup_logger, get_project_root, storage_cached

logger = setup_logger('LLMService')


class LLMService(ABC):
    def __init__(self, config):
        self.config = config

    def clean_response_text(self, response_text: str):
        return response_text.replace("\n", "")

    def get_prompt(self, search_text: str, gpt_input_text_df: pd.DataFrame):
        logger.info(f"OpenAIService.get_prompt. search_text: {search_text}, gpt_input_text_df.shape: {gpt_input_text_df.shape}")
        prompt_length_limit = self.config.get('llm_service').get('openai_api').get('prompt').get('prompt_length_limit')
        is_use_source = self.config.get('source_service').get('is_use_source')
        if is_use_source:
            prompt_engineering = f"\n\nAnswer the question '{search_text}' using above information with about 100 words:"
            prompt = ""
            for index, row in gpt_input_text_df.iterrows():
                prompt += f"""{row['text']}\n"""
            # limit the prompt length
            prompt = prompt[:prompt_length_limit]
            return prompt + prompt_engineering
        else:
            return f"\n\nAnswer the question '{search_text}' with about 100 words:"

    def get_prompt_v2(self, search_text: str, gpt_input_text_df: pd.DataFrame):
        logger.info(f"OpenAIService.get_prompt_v2. search_text: {search_text}, gpt_input_text_df.shape: {gpt_input_text_df.shape}")
        context_str = ""
        gpt_input_text_df = gpt_input_text_df.sort_values('url_id')
        url_id_list = gpt_input_text_df['url_id'].unique()
        for url_id in url_id_list:
            context_str += f"Source ({url_id})\n"
            for index, row in gpt_input_text_df[gpt_input_text_df['url_id'] == url_id].iterrows():
                context_str += f"{row['text']}\n"
            context_str += "\n"
        prompt_length_limit = self.config.get('llm_service').get('openai_api').get('prompt').get('prompt_length_limit')
        context_str = context_str[:prompt_length_limit]
        prompt = \
            f"""
Answer with 100 words for the question below based on the provided sources using a scientific tone. 
If the context is insufficient, reply "I cannot answer".
Use Markdown for formatting code or text.
Source:
{context_str}
Question: {search_text}
Answer:
"""
        return prompt

    def get_prompt_v3(self, search_text: str, gpt_input_text_df: pd.DataFrame):
        if not self.config.get('source_service').get('is_use_source'):
            prompt = \
                f"""
Instructions: Write a comprehensive reply to the given query.  
If the context is insufficient, reply "I cannot answer".
Query: {search_text}
"""
            return prompt

        logger.info(f"OpenAIService.get_prompt_v3. search_text: {search_text}, gpt_input_text_df.shape: {gpt_input_text_df.shape}")
        context_str = ""
        for _, row_url in gpt_input_text_df[['url_id', 'url']].drop_duplicates().iterrows():
            domain = urlparse(row_url['url']).netloc.replace('www.', '')
            context_str += f"Source [{row_url['url_id']}] {domain}\n"
            for index, row in gpt_input_text_df[(gpt_input_text_df['url_id'] == row_url['url_id']) & gpt_input_text_df['in_scope']].iterrows():
                context_str += f"{row['text']}\n"
            context_str += "\n\n"
        prompt_length_limit = self.config.get('llm_service').get('openai_api').get('prompt').get('prompt_length_limit')
        context_str = context_str[:prompt_length_limit]
        prompt = \
            f"""
Web search result:
{context_str}

Instructions: Using the provided web search results, write a comprehensive reply to the given query. 
Make sure to cite results using [number] notation after the reference.
If the provided search results refer to multiple subjects with the same name, write separate answers for each subject. 
If the context is insufficient, reply "I cannot answer because my reference sources don't have related info".
Query: {search_text}
"""
        return prompt

    @abstractmethod
    def call_api(self, prompt):
        pass


class OpenAIService(LLMService):
    def __init__(self, config):
        super().__init__(config)
        open_api_key = config.get('llm_service').get('openai_api').get('api_key')
        if open_api_key is None:
            raise Exception("OpenAI API key is not set.")
        openai.api_key = open_api_key

    @storage_cached('openai', 'prompt')
    def call_api(self, prompt: str):
        openai_api_config = self.config.get('llm_service').get('openai_api')
        model = openai_api_config.get('model')
        logger.info(f"OpenAIService.call_api. model: {model}, len(prompt): {len(prompt)}")

        if model == 'gpt-3.5-turbo':
            try:
                completion = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
            except Exception as ex:
                raise ex
            return completion.choices[0].message.content
        else:
            try:
                response = openai.Completion.create(
                    model=model,
                    prompt=prompt,
                    max_tokens=openai_api_config.get('max_tokens'),
                    temperature=openai_api_config.get('temperature'),
                    top_p=openai_api_config.get('top_p'),
                )
            except Exception as ex:
                raise ex
            return self.clean_response_text(response.choices[0].text)

    def call_streaming_api(self, prompt: str):
        openai_api_config = self.config.get('llm_service').get('openai_api')
        model = openai_api_config.get('model')
        logger.info(f"OpenAIService.call_api. model: {model}, len(prompt): {len(prompt)}")

        if model == 'gpt-3.5-turbo':
            try:
                completion = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    stream=True
                )
                print('=========Source=========')
                print(prompt)
                print(f"=========Response model:{model}=========")
                for c in completion:
                    if c.choices[0]['delta'].get('content'):
                        print(c.choices[0]['delta'].get('content'), end='')
                print("")
            except Exception as ex:
                raise ex
        else:
            try:
                completion = openai.Completion.create(
                    model=model,
                    prompt=prompt,
                    max_tokens=openai_api_config.get('max_tokens'),
                    temperature=openai_api_config.get('temperature'),
                    top_p=openai_api_config.get('top_p'),
                    stream=True
                )
                print('=========Source=========')
                print(prompt)
                print(f"=========Response model:{model}=========")
                for c in completion:
                    if c.choices[0]['delta'].get('content'):
                        print(c.choices[0]['delta'].get('content'), end='')
                print("")
            except Exception as ex:
                raise ex


class GooseAIService(LLMService):
    def __init__(self, config):
        super().__init__(config)
        self.goose_api_config = self.config.get('llm_service').get('goose_ai_api')
        goose_api_key = self.goose_api_config.get('api_key')
        if goose_api_key is None:
            raise Exception("Goose API key is not set.")
        openai.api_key = goose_api_key
        openai.api_base = self.goose_api_config.get('api_base')

    @storage_cached('gooseai', 'prompt')
    def call_api(self, prompt: str):
        logger.info(f"GooseAIService.call_openai_api. len(prompt): {len(prompt)}")
        try:
            response = openai.Completion.create(
                engine=self.goose_api_config.get('model'),
                prompt=prompt,
                max_tokens=self.goose_api_config.get('max_tokens'),
                # stream=True
            )
        except Exception as ex:
            raise ex
        return self.clean_response_text(response.choices[0].text)

    def call_streaming_api(self, prompt: str):
        logger.info(f"GooseAIService.call_openai_api. len(prompt): {len(prompt)}")
        try:
            response = openai.Completion.create(
                engine=self.goose_api_config.get('model'),
                prompt=prompt,
                max_tokens=self.goose_api_config.get('max_tokens'),
                stream=True
            )
            print('=========Source=========')
            print(prompt)
            print(f"=========Response model:{self.goose_api_config.get('model')}=========")
            for c in response:
                print(c.choices[0].text, end='')
            print("")
        except Exception as ex:
            raise ex


class LLMServiceFactory:
    @staticmethod
    def create_llm_service(config) -> LLMService:
        provider = config.get('llm_service').get('provider')
        if provider == 'openai':
            return OpenAIService(config)
        elif provider == 'goose_ai':
            return GooseAIService(config)
        else:
            logger.error(f'LLM Service for {provider} is not yet implemented.')
            raise NotImplementedError(f'LLM Service - {provider} - not is supported')


if __name__ == '__main__':
    # Load config
    with open(os.path.join(get_project_root(), 'src/config/config.yaml')) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        service_factory = LLMServiceFactory()
        service: LLMService = service_factory.create_llm_service(config)
        prompt = """
Source:
In Greek mythology, Achilles ( ) or Achilleus () was a hero of the Trojan War, the greatest of all the Greek warriors, and is the central character of Homer's Iliad. He was the son of the Nereid Thetis and Peleus, king of Phthia.
Achilles' most notable feat during the Trojan War was the slaying of the Trojan prince Hector outside the gates of Troy. Although the death of Achilles is not presented in the Iliad, other sources concur that he was killed near the end of the Trojan War by Paris, who shot him with an arrow. Later legends (beginning with Statius' unfinished epic Achilleid, written in the 1st century AD) state that Achilles was invulnerable in all of his body except for one heel, because when his mother Thetis dipped him in the river Styx as an infant, she held him by one of his heels. Alluding to these legends, the term "Achilles' heel" has come to mean a point of weakness, especially in someone or something with an otherwise strong constitution. The Achilles tendon is also named after him due to these legends.
Etymology
Linear B tablets attest to the personal name Achilleus in the forms a-ki-re-u and a-ki-re-we, the latter being the dative of the former. The name grew more popular, even becoming common soon after the seventh century BC and was also turned into the female form Ἀχιλλεία (Achilleía), attested in Attica in the fourth century BC (IG II² 1617) and, in the form Achillia, on a stele in Halicarnassus as the name of a female gladiator fighting an "Amazon".
Achilles' name can be analyzed as a combination of () "distress, pain, sorrow, grief" and () "people, soldiers, nation", resulting in a proto-form *Akhí-lāu̯os "he who has the people distressed" or "he whose people have distress". The grief or distress of the people is a theme raised numerous times in the Iliad (and frequently by Achilles himself). Achilles' role as the hero of grief or distress forms an ironic juxtaposition with the conventional view of him as the hero of ("glory", usually in war). Furthermore, laós has been construed by Gregory Nagy, following Leonard Palmer, to mean "a corps of soldiers", a muster. With this derivation, the name obtains a double meaning in the poem: when the hero is functioning rightly, his men bring distress to the enemy, but when wrongly, his men get the grief of war. The poem is in part about the misdirection of anger on the part of leadership.
Another etymology relates the name to a Proto-Indo-European compound *h₂eḱ-pṓds "sharp foot" which first gave an Illyrian *āk̂pediós, evolving through time into *ākhpdeós and then *akhiddeús. The shift from -dd- to -ll- is then ascribed to the passing of the name into Greek via a Pre-Greek source. The first root part *h₂eḱ- "sharp, pointed" also gave Greek ἀκή (akḗ "point, silence, healing"), ἀκμή (akmḗ "point, edge, zenith") and ὀξύς (oxús "sharp,

Instructions: Using the provided source, write a comprehensive reply to the given query with 80 words.
Query: Who is Achilles
Answer: 
        """
        response_text = service.call_streaming_api(prompt=prompt)
        print(response_text)

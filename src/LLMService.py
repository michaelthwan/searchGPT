from abc import ABC, abstractmethod
import openai
import pandas as pd
import yaml

from Util import setup_logger

logger = setup_logger('LLMService')


class LLMService(ABC):
    def __init__(self, config):
        self.config = config

    def clean_response_text(self, response_text: str):
        return response_text.replace("\n", "")

    def get_prompt(self, search_text: str, gpt_input_text_df: pd.DataFrame):
        logger.info(f"OpenAIService.get_prompt. search_text: {search_text}, gpt_input_text_df.shape: {gpt_input_text_df.shape}")
        prompt_length_limit = self.config.get('openai_api').get('prompt').get('prompt_length_limit')
        is_use_source = self.config.get('search_option').get('is_use_source')
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
        prompt_length_limit = self.config.get('openai_api').get('prompt').get('prompt_length_limit')
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

    @abstractmethod
    def call_api(self, prompt):
        pass


class OpenAIService(LLMService):
    def __init__(self, config):
        super().__init__(config)
        open_api_key = config.get('openai_api').get('api_key')
        if open_api_key is None:
            raise Exception("OpenAI API key is not set.")
        openai.api_key = open_api_key

    def call_api(self, prompt: str):
        openai_api_config = self.config.get('openai_api')
        model = openai_api_config.get('model')
        logger.info(f"OpenAIService.call_api. model: {model}, len(prompt): {len(prompt)}")

        if model == 'gpt-3.5-turbo':
            try:
                completion = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful search engine."},
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


class GooseAIService(LLMService):
    def __init__(self, config):
        super().__init__(config)
        goose_api_key = config.get('goose_ai_api').get('api_key')
        if goose_api_key is None:
            raise Exception("Goose API key is not set.")
        openai.api_key = goose_api_key
        openai.api_base = config.get('goose_ai_api').get('api_base')

    def call_api(self, prompt: str):
        logger.info(f"GooseAIService.call_openai_api. len(prompt): {len(prompt)}")
        goose_api_config = self.config.get('goose_ai_api')
        try:
            response = openai.Completion.create(
                engine=goose_api_config.get('model'),
                prompt=prompt,
                max_tokens=goose_api_config.get('max_tokens'),
                # stream=True
            )
        except Exception as ex:
            raise ex
        return self.clean_response_text(response.choices[0].text)


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
    with open('config/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        service_factory = LLMServiceFactory()
        service = service_factory.create_llm_service(config)
        prompt = """
        """
        # response_text = service.call_openai_api('What is ChatGPT')
        response_text = service.call_api(prompt)
        print(response_text)
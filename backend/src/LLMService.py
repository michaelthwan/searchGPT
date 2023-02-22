from abc import ABC, abstractmethod
import openai
import pandas as pd
import yaml

from Util import setup_logger

logger = setup_logger('OpenAIService')


class LLMService(ABC):
    def __init__(self, config):
        self.config = config

    def clean_response_text(self, response_text: str):
        return response_text.replace("\n", "")

    def get_prompt(self, search_text: str, gpt_input_text_df: pd.DataFrame):
        logger.info(f"OpenAIService.get_prompt. search_text: {search_text}, gpt_input_text_df.shape: {gpt_input_text_df.shape}")
        prompt_length_limit = self.config.get('openai_api').get('prompt').get('prompt_length_limit')
        prompt_engineering = f"\n\nSummarize the question '{search_text}' using above information with about 80 words:"
        prompt = ""
        for index, row in gpt_input_text_df.iterrows():
            prompt += f"""{row['text']}\n"""
        # limit the prompt length
        prompt = prompt[:prompt_length_limit]
        return prompt + prompt_engineering

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
        logger.info(f"OpenAIService.call_openai_api. len(prompt): {len(prompt)}")
        openai_api_config = self.config.get('openai_api')
        try:
            response = openai.Completion.create(
                model=openai_api_config.get('model'),
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
    def creaet_llm_service(config) -> LLMService:
        provider = config.get('llm_service').get('provider')
        if provider == 'openai':
            return OpenAIService(config)
        elif provider == 'goose_ai':
            return GooseAIService(config)
        else:
            logger.error(f'LLM Service for {provider} not yet implemented.')
            raise ValueError('LLM Service - {provider} - not suppported')


if __name__ == '__main__':
    # Load config
    with open('config/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        service_factory = LLMServiceFactory()
        service = service_factory.creaet_llm_service(config)
        prompt = """
[1] What is 'Wordle'? Here's everything you need to know - mashable.com
What is Wordle?
Yeah, I just said this is an easy question to answer. But for the sake of completeness, let's start with the basics.

Wordle is a daily word game(Opens in a new tab) created by Josh Wardle, a Brooklyn-based software engineer who has developed something of a reputation as a crafter of(Opens in a new tab) interesting social experiments(Opens in a new tab). Every day, the people of the internet are greeted with a fresh word puzzle that can only be solved â€or not! â€using a series of process-of-elimination clues.

[2] What Is Wordle? All the Details on the Viral New Word Gameâ€”And How to Play It - parade.com
What is Wordle?
Wordle is an addictive online word game that you can play daily here. There is only one puzzle per day
Examples of good Wordle starting wordsare "STARE," "TEARS," "NOTES," "RESIN," "STORE," "RIOTS," "STAIN," and "SNORE."

[3] Our 4 tips for winning Wordle every day - pcgamer.com
Wordle tips
Want to play Wordle? Of course you do. But if there's one thing better than playing Wordle, it's playing Wordle well, which is why I'm going to share a few quick tips to help set you on the path to word-puzzling success:

Begin with a word that uses several different vowels and common consonants. ALERT, RAISE, and MILES are all good examples, but anything along those lines will do the job just as well. ATAXY, on the other hand, uses A twice and has an X and Y which, if eliminated, probably won't help you with your next guess all that much

[4] â€˜Whatâ€™s Wordle?â€and your other Wordle questions, answered - washingtonpost.com
Wordle is just a word deduction game, but its simple nature belies the fact that it has â€in the span of just a few weeks â€become a phenomenon. Maybe youâ€™re here because you were enticed by the strange green and yellow squares on social media. Maybe you just saw the New York Times is acquiring the popular word game for an undisclosed seven figure price tag

Tl;dr with 40 words
        """
        # response_text = service.call_openai_api('What is ChatGPT')
        response_text = service.call_api(prompt)
        print(response_text)

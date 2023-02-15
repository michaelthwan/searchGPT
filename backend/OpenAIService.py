import openai
import yaml


class OpenAIService:
    def __init__(self, config):
        self.config = config
        openai.api_key = config['openai_api']['api_key']

    def call_openai_api(self, prompt: str):
        openai_api_config = config['openai_api']
        response = openai.Completion.create(
            model=openai_api_config['model'],
            prompt=prompt,
            max_tokens=openai_api_config['max_tokens'],
            temperature=openai_api_config['temperature'],
            top_p=openai_api_config['top_p'],
        )
        return response.choices[0].text


if __name__ == '__main__':
    # Load config
    with open('config/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        service = OpenAIService(config)
        response_text = service.call_openai_api('What is ChatGPT')
        print(response_text)

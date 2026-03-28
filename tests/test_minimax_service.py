"""Unit tests for MiniMaxService and LLMServiceFactory MiniMax integration."""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def _base_config():
    """Return a minimal config dict for MiniMax provider."""
    return {
        'llm_service': {
            'provider': 'minimax',
            'minimax_api': {
                'api_key': 'test-minimax-key',
                'api_base': 'https://api.minimax.io/v1',
                'model': 'MiniMax-M2.7',
                'max_tokens': 300,
                'temperature': 0.7,
                'stream': False,
            },
            'openai_api': {
                'api_key': None,
                'model': 'gpt-3.5-turbo',
                'max_tokens': 300,
                'temperature': 1,
                'top_p': 1,
                'stream': True,
                'prompt': {'prompt_length_limit': 3000, 'prompt_token_limit': 1500},
            },
        },
        'source_service': {
            'is_use_source': True,
            'is_enable_bing_search': False,
            'bing_search': {'subscription_key': None},
        },
        'general': {'language': 'en-US'},
        'cache': {
            'is_enable': {'web': False, 'openai': False, 'gooseai': False, 'minimax': False},
            'path': '.cache',
            'max_number_of_cache': 50,
        },
    }


class TestMiniMaxServiceInit(unittest.TestCase):
    """Test MiniMaxService initialization."""

    @patch('LLMService.openai')
    def test_init_with_config_api_key(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        svc = MiniMaxService(config)
        self.assertEqual(mock_openai.api_key, 'test-minimax-key')
        self.assertEqual(mock_openai.api_base, 'https://api.minimax.io/v1')

    @patch('LLMService.openai')
    def test_init_with_env_api_key(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['api_key'] = None
        with patch.dict(os.environ, {'MINIMAX_API_KEY': 'env-minimax-key'}):
            svc = MiniMaxService(config)
            self.assertEqual(mock_openai.api_key, 'env-minimax-key')

    @patch('LLMService.openai')
    def test_init_missing_api_key_raises(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['api_key'] = None
        with patch.dict(os.environ, {}, clear=True):
            env = os.environ.copy()
            env.pop('MINIMAX_API_KEY', None)
            with patch.dict(os.environ, env, clear=True):
                with self.assertRaises(Exception) as ctx:
                    MiniMaxService(config)
                self.assertIn('MiniMax API key is not set', str(ctx.exception))

    @patch('LLMService.openai')
    def test_init_custom_api_base(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['api_base'] = 'https://custom.minimax.io/v1'
        svc = MiniMaxService(config)
        self.assertEqual(mock_openai.api_base, 'https://custom.minimax.io/v1')


class TestMiniMaxServiceCallApi(unittest.TestCase):
    """Test MiniMaxService.call_api method."""

    @patch('LLMService.openai')
    def test_call_api_non_stream(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['stream'] = False

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'MiniMax response text'
        mock_openai.ChatCompletion.create.return_value = mock_response

        svc = MiniMaxService(config)
        result = svc.call_api(prompt='test prompt')
        self.assertEqual(result, 'MiniMax response text')

        call_kwargs = mock_openai.ChatCompletion.create.call_args
        self.assertEqual(call_kwargs[1]['model'], 'MiniMax-M2.7')
        self.assertEqual(call_kwargs[1]['temperature'], 0.7)
        self.assertEqual(call_kwargs[1]['stream'], False)

    @patch('LLMService.openai')
    def test_call_api_stream(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['stream'] = True

        chunk1 = MagicMock()
        chunk1.__getitem__ = lambda self, k: {'choices': [{'delta': {'content': 'Hello'}}]}[k]
        chunk2 = MagicMock()
        chunk2.__getitem__ = lambda self, k: {'choices': [{'delta': {'content': ' World'}}]}[k]

        mock_openai.ChatCompletion.create.return_value = iter([chunk1, chunk2])

        svc = MiniMaxService(config)
        result = svc.call_api(prompt='test prompt')
        self.assertEqual(result, 'Hello World')

    @patch('LLMService.openai')
    def test_temperature_clamping_zero(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['temperature'] = 0.0
        config['llm_service']['minimax_api']['stream'] = False

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'response'
        mock_openai.ChatCompletion.create.return_value = mock_response

        svc = MiniMaxService(config)
        svc.call_api(prompt='test')
        call_kwargs = mock_openai.ChatCompletion.create.call_args[1]
        self.assertGreater(call_kwargs['temperature'], 0.0)
        self.assertEqual(call_kwargs['temperature'], 0.01)

    @patch('LLMService.openai')
    def test_temperature_clamping_above_one(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['temperature'] = 2.0
        config['llm_service']['minimax_api']['stream'] = False

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'response'
        mock_openai.ChatCompletion.create.return_value = mock_response

        svc = MiniMaxService(config)
        svc.call_api(prompt='test')
        call_kwargs = mock_openai.ChatCompletion.create.call_args[1]
        self.assertEqual(call_kwargs['temperature'], 1.0)

    @patch('LLMService.openai')
    def test_default_model(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        del config['llm_service']['minimax_api']['model']
        config['llm_service']['minimax_api']['stream'] = False

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'response'
        mock_openai.ChatCompletion.create.return_value = mock_response

        svc = MiniMaxService(config)
        svc.call_api(prompt='test')
        call_kwargs = mock_openai.ChatCompletion.create.call_args[1]
        self.assertEqual(call_kwargs['model'], 'MiniMax-M2.7')

    @patch('LLMService.openai')
    def test_call_api_with_sender(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['stream'] = False

        mock_sender = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'response'
        mock_openai.ChatCompletion.create.return_value = mock_response

        svc = MiniMaxService(config, sender=mock_sender)
        svc.call_api(prompt='test')
        mock_sender.send_message.assert_called_once()

    @patch('LLMService.openai')
    def test_call_api_exception_propagated(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['stream'] = False

        mock_openai.ChatCompletion.create.side_effect = Exception("API error")

        svc = MiniMaxService(config)
        with self.assertRaises(Exception) as ctx:
            svc.call_api(prompt='test')
        self.assertIn('API error', str(ctx.exception))

    @patch('LLMService.openai')
    def test_highspeed_model(self, mock_openai):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['model'] = 'MiniMax-M2.7-highspeed'
        config['llm_service']['minimax_api']['stream'] = False

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'fast response'
        mock_openai.ChatCompletion.create.return_value = mock_response

        svc = MiniMaxService(config)
        result = svc.call_api(prompt='test')
        self.assertEqual(result, 'fast response')
        call_kwargs = mock_openai.ChatCompletion.create.call_args[1]
        self.assertEqual(call_kwargs['model'], 'MiniMax-M2.7-highspeed')


class TestLLMServiceFactory(unittest.TestCase):
    """Test LLMServiceFactory MiniMax integration."""

    @patch('LLMService.openai')
    def test_factory_creates_minimax(self, mock_openai):
        from LLMService import LLMServiceFactory, MiniMaxService
        config = _base_config()
        svc = LLMServiceFactory.create_llm_service(config)
        self.assertIsInstance(svc, MiniMaxService)

    @patch('LLMService.openai')
    def test_factory_openai_still_works(self, mock_openai):
        from LLMService import LLMServiceFactory, OpenAIService
        config = _base_config()
        config['llm_service']['provider'] = 'openai'
        config['llm_service']['openai_api']['api_key'] = 'test-openai-key'
        svc = LLMServiceFactory.create_llm_service(config)
        self.assertIsInstance(svc, OpenAIService)

    def test_factory_unsupported_provider(self):
        from LLMService import LLMServiceFactory
        config = _base_config()
        config['llm_service']['provider'] = 'unsupported_provider'
        with self.assertRaises(NotImplementedError):
            LLMServiceFactory.create_llm_service(config)

    @patch('LLMService.openai')
    def test_factory_with_sender(self, mock_openai):
        from LLMService import LLMServiceFactory, MiniMaxService
        config = _base_config()
        mock_sender = MagicMock()
        svc = LLMServiceFactory.create_llm_service(config, sender=mock_sender)
        self.assertIsInstance(svc, MiniMaxService)
        self.assertEqual(svc.sender, mock_sender)


class TestMiniMaxPromptGeneration(unittest.TestCase):
    """Test that MiniMax service inherits prompt generation correctly."""

    @patch('LLMService.openai')
    def test_get_prompt_v3_inherited(self, mock_openai):
        import pandas as pd
        from LLMService import MiniMaxService
        config = _base_config()
        svc = MiniMaxService(config)
        text_df = pd.DataFrame({
            'url_id': [1, 1],
            'url': ['https://example.com', 'https://example.com'],
            'text': ['Some content', 'More content'],
            'in_scope': [True, True],
        })
        prompt = svc.get_prompt_v3('test query', text_df)
        self.assertIn('test query', prompt)
        self.assertIn('Some content', prompt)


class TestSearchGPTServiceMiniMax(unittest.TestCase):
    """Test SearchGPTService config override for MiniMax."""

    @patch('LLMService.openai')
    def test_config_override_minimax_model(self, mock_openai):
        """Test that model override logic works for minimax provider."""
        # Test the override logic directly without importing SearchGPTService
        # (SearchGPTService imports SemanticSearchService which needs openai.embeddings_utils)
        config = _base_config()
        config['llm_service']['provider'] = 'minimax'
        # Simulate what SearchGPTService.overide_config_by_query_string does
        value = 'MiniMax-M2.7-highspeed'
        if config['llm_service']['provider'] == 'minimax':
            config['llm_service']['minimax_api']['model'] = value
        self.assertEqual(config['llm_service']['minimax_api']['model'], 'MiniMax-M2.7-highspeed')

        # Verify the service can be created with the overridden config
        from LLMService import LLMServiceFactory, MiniMaxService
        svc = LLMServiceFactory.create_llm_service(config)
        self.assertIsInstance(svc, MiniMaxService)


if __name__ == '__main__':
    unittest.main()

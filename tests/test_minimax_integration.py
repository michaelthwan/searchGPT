"""Integration tests for MiniMax LLM service (requires MINIMAX_API_KEY and openai<1.0.0)."""
import os
import sys
import unittest

import openai

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# This project uses openai==0.27.0 (legacy API). Skip if openai>=1.0.0 is installed.
_openai_legacy = not hasattr(openai, 'lib')  # openai>=1.0 has openai.lib module


def _base_config():
    """Return config dict for MiniMax provider using env API key."""
    return {
        'llm_service': {
            'provider': 'minimax',
            'minimax_api': {
                'api_key': None,  # Will use MINIMAX_API_KEY env var
                'api_base': 'https://api.minimax.io/v1',
                'model': 'MiniMax-M2.7',
                'max_tokens': 100,
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
            'is_use_source': False,
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


@unittest.skipUnless(os.environ.get('MINIMAX_API_KEY'), 'MINIMAX_API_KEY not set')
@unittest.skipUnless(_openai_legacy, 'Requires openai<1.0.0 (project uses openai==0.27.0)')
class TestMiniMaxIntegration(unittest.TestCase):
    """Integration tests that call the real MiniMax API."""

    def test_non_stream_response(self):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['stream'] = False
        svc = MiniMaxService(config)
        result = svc.call_api(prompt='Say "hello" in one word.')
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_stream_response(self):
        from LLMService import MiniMaxService
        config = _base_config()
        config['llm_service']['minimax_api']['stream'] = True
        svc = MiniMaxService(config)
        result = svc.call_api(prompt='Say "hello" in one word.')
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_factory_integration(self):
        from LLMService import LLMServiceFactory, MiniMaxService
        config = _base_config()
        svc = LLMServiceFactory.create_llm_service(config)
        self.assertIsInstance(svc, MiniMaxService)
        result = svc.call_api(prompt='What is 1+1? Answer with just the number.')
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()

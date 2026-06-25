from ..config.settings import settings
from .adapters.openai_adapter import OpenAIAdapter
from .adapters.ollama_adapter import OllamaAdapter

class LLMFactory:
    """
    Factory to create the appropriate LLM adapter based on configuration.
    """

    @staticmethod
    def get_adapter():
        """
        Returns an LLM adapter instance based on the current settings.
        """
        # Check if Ollama is explicitly enabled in settings
        # Note: In a real implementation, we'd check a more granular provider setting.
        # For now, if api_base contains 'localhost' or 'ollama', we assume Ollama.

        if "localhost" in settings.llm.api_base or "127.0.0.1" in settings.llm.api_base:
            return OllamaAdapter()

        return OpenAIAdapter()

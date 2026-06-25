from .openai_adapter import OpenAIAdapter
from ...config.settings import settings

class OllamaAdapter(OpenAIAdapter):
    """
    Ollama provider adapter for the LLM interface.
    Specializes in targeting the local Ollama endpoint.
    """

    def __init__(self):
        # Use the base URL from settings, which defaults to Ollama
        super().__init__()
        # Ensure we are using the Ollama base URL if provided in settings
        self.api_base = settings.llm.api_base
        # Re-initialize the LLM with the correct base URL
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=self.api_key,
            base_url=self.api_base
        )

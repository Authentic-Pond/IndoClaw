from typing import List, Dict, Optional, Iterator
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from ..llm_adapter_base import BaseLLMAdapter
from ...config.settings import settings

class OpenAIAdapter(BaseLLMAdapter):
    """
    OpenAI provider adapter for the LLM interface.
    Supports ChatOpenAI for text generation and OpenAIEmbeddings for embeddings.
    """

    def __init__(self):
        self.model_name = settings.llm.model_name
        self.temperature = settings.llm.temperature
        self.api_key = settings.llm.api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = settings.llm.api_base

        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in environment or config.")

        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=self.api_key,
            base_url=self.api_base if self.api_base != "https://api.openai.com/v1" else None
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.llm.embedding_model,
            openai_api_key=self.api_key,
            base_url=self.api_base if self.api_base != "https://api.openai.com/v1" else None
        )

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List:
        """Convert message dict to LangChain message objects."""
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "").lower()
            content = msg.get("content", "")
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))
        return langchain_messages

    def generate(self, prompt: str) -> str:
        """Generate a simple text response from a prompt."""
        return self.chat([{"role": "user", "content": prompt}])

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response based on a list of chat messages."""
        langchain_messages = self._convert_messages(messages)
        response = self.llm.invoke(langchain_messages)
        return response.content

    def embed(self, text: str) -> List[float]:
        """Create a vector embedding for the provided text."""
        return self.embeddings.embed_query(text)

    def stream(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        """Stream the response from the LLM."""
        langchain_messages = self._convert_messages(messages)
        for chunk in self.llm.stream(langchain_messages):
            yield chunk.content

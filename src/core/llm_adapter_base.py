from abc import ABC, abstractmethod
from typing import List, Dict

class BaseLLMAdapter(ABC):
    """
    Abstract base class for all LLM provider adapters.
    Ensaryies a consistent interface for generating text and embeddings
    regardless of the underlying provider (OpenAI, Ollama, etc.).
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a simple text response from a prompt.

        Args:
            prompt: The input text.

        Returns:
            The generated text response.
        """
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response based on a list of chat messages.

        Args:
            messages: A list of dictionaries containing 'role' and 'content'.
                       e.g., [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]

        Returns:
            The generated text response.
        """
        pass

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Create a vector embedding for the provided text.

        Args:
            text: The input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        pass

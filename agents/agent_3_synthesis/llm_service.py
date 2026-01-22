"""
LLM Service for Agent 3.
Provides interface to LLM services including Otoroshi.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import json
import httpx
from loguru import logger

from config import get_settings


class LLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """Generate text completion."""
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """Generate chat completion."""
        pass


class OtoroshiLLMService(LLMService):
    """
    LLM Service using Otoroshi API gateway.
    Supports various LLM backends through Otoroshi's routing.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "default",
        timeout: float = 60.0,
    ):
        """
        Initialize Otoroshi LLM service.
        
        Args:
            api_url: Otoroshi API endpoint
            api_key: API key for authentication
            model: Model identifier
            timeout: Request timeout in seconds
        """
        self.settings = get_settings()
        self.api_url = api_url or self.settings.otoroshi_api_url
        self.api_key = api_key or self.settings.otoroshi_api_key
        self.model = model
        self.timeout = timeout
        
        self._logger = logger.bind(component="OtoroshiLLMService")
        self._client = httpx.Client(timeout=timeout)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """
        Generate text completion via Otoroshi.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat(messages, max_tokens, temperature)

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """
        Generate chat completion via Otoroshi.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Assistant's response text
        """
        self._logger.info(f"Sending chat request to Otoroshi ({len(messages)} messages)")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        try:
            response = self._client.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract response text (OpenAI-compatible format)
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
            
            self._logger.warning(f"Unexpected response format: {result}")
            return ""
            
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self._logger.error(f"Request failed: {e}")
            raise

    def close(self):
        """Close the HTTP client."""
        self._client.close()


class OpenAILLMService(LLMService):
    """
    LLM Service using OpenAI API directly.
    Fallback option when Otoroshi is not available.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
    ):
        """
        Initialize OpenAI LLM service.
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o-mini)
        """
        self.settings = get_settings()
        self.api_key = api_key or self.settings.openai_api_key
        self.model = model
        
        self._logger = logger.bind(component="OpenAILLMService")
        self._client = None

    def _get_client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("Please install openai: pip install openai")
        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """Generate text completion."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat(messages, max_tokens, temperature)

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """Generate chat completion."""
        self._logger.info(f"Sending chat request to OpenAI ({len(messages)} messages)")
        
        client = self._get_client()
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return response.choices[0].message.content

    def close(self):
        """Close resources."""
        self._client = None


class OllamaLLMService(LLMService):
    """
    LLM Service using Ollama API.
    Supports Llama and other models available locally.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 300.0,
    ):
        """
        Initialize Ollama LLM service.
        
        Args:
            api_url: Ollama API endpoint
            model: Model identifier (e.g., 'llama2', 'mistral')
            timeout: Request timeout in seconds
        """
        self.settings = get_settings()
        self.api_url = api_url or self.settings.ollama_api_url
        self.model = model or self.settings.ollama_model
        self.timeout = timeout
        
        self._logger = logger.bind(component="OllamaLLMService")
        self._client = httpx.Client(timeout=timeout)
        
        self._logger.info(f"Initialized Ollama service at {self.api_url} with model {self.model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """
        Generate text completion via Ollama.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "temperature": temperature,
                "num_predict": max_tokens,
            }
            
            response = self._client.post(
                f"{self.api_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except Exception as e:
            self._logger.error(f"Ollama generation error: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """
        Generate chat completion via Ollama.
        
        Args:
            messages: List of chat messages
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "temperature": temperature,
                "num_predict": max_tokens,
            }
            
            response = self._client.post(
                f"{self.api_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "").strip()
            
        except Exception as e:
            self._logger.error(f"Ollama chat error: {e}")
            raise

    def close(self):
        """Close the HTTP client."""
        self._client.close()


class MockLLMService(LLMService):
    """
    Mock LLM service for testing without API calls.
    Generates contextual responses based on the provided context.
    """

    def __init__(self):
        self._logger = logger.bind(component="MockLLMService")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """Return mock response based on context."""
        self._logger.info("MockLLMService: Generating contextual response")
        return self._extract_answer_from_context(prompt)

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """Return mock chat response based on context."""
        self._logger.info(f"MockLLMService: Mock chat with {len(messages)} messages")
        
        # Find the user question and context
        last_user_msg = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break
        
        return self._extract_answer_from_context(last_user_msg)

    def _extract_answer_from_context(self, prompt: str) -> str:
        """
        Extract relevant information from the context in the prompt.
        Creates a readable response from the retrieved chunks.
        """
        # Check if there's context in the prompt
        if "CONTEXTE:" in prompt or "Context:" in prompt:
            # Extract the context section
            context_start = prompt.find("CONTEXTE:")
            if context_start == -1:
                context_start = prompt.find("Context:")
            
            question_start = prompt.find("QUESTION:")
            if question_start == -1:
                question_start = prompt.find("Question:")
            
            if context_start != -1:
                # Extract context
                if question_start != -1 and question_start > context_start:
                    context = prompt[context_start:question_start].strip()
                else:
                    context = prompt[context_start:].strip()
                
                # Clean up context
                context = context.replace("CONTEXTE:", "").replace("Context:", "").strip()
                
                # Extract question
                question = ""
                if question_start != -1:
                    question = prompt[question_start:].split("\n")[0]
                    question = question.replace("QUESTION:", "").replace("Question:", "").strip()
                
                # Build a structured response
                response_parts = []
                response_parts.append(f"Basé sur les documents analysés, voici ce que j'ai trouvé :\n")
                
                # Parse chunks from context
                chunks = context.split("---")
                relevant_info = []
                
                for chunk in chunks:
                    chunk = chunk.strip()
                    if len(chunk) > 50:  # Only meaningful chunks
                        # Extract key sentences
                        sentences = chunk.split(".")
                        for sentence in sentences[:3]:  # First 3 sentences
                            sentence = sentence.strip()
                            if len(sentence) > 30:
                                relevant_info.append(sentence + ".")
                
                if relevant_info:
                    response_parts.append("\n".join(relevant_info[:5]))  # Top 5 relevant sentences
                else:
                    response_parts.append(context[:500])  # Fallback to raw context
                
                return "\n\n".join(response_parts)
        
        # Fallback for prompts without context
        return f"⚠️ Mode Mock actif - Pas de LLM configuré.\n\nPour de vraies réponses, utilisez:\n  python3 main.py --interactive --llm ollama\n  ou\n  python3 main.py --interactive --llm openai\n\nQuestion reçue: {prompt[:200]}..."

    def close(self):
        pass


def get_llm_service(
    service_type: str = "otoroshi",
    **kwargs
) -> LLMService:
    """
    Factory function to get appropriate LLM service.
    
    Args:
        service_type: Type of service ('ollama', 'otoroshi', 'openai', 'mock')
        **kwargs: Additional arguments for the service
        
    Returns:
        LLMService instance
    """
    services = {
        "ollama": OllamaLLMService,
        "otoroshi": OtoroshiLLMService,
        "openai": OpenAILLMService,
        "mock": MockLLMService,
    }
    
    service_class = services.get(service_type.lower())
    
    if not service_class:
        raise ValueError(f"Unknown LLM service type: {service_type}")
    
    return service_class(**kwargs)

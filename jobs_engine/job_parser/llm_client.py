"""This module is used to create a Job offer text parser using LLMs."""

import json
import os
from typing import Optional

import requests
from django.conf import settings


class LLMClient:
    """A client to interact with multiple LLM APIs."""

    def __init__(
        self,
        default_together_model: str = "meta-llama/Llama-3.2-3B-Instruct-Turbo",
        temperature: float = 0.7,
        max_tokens: int = 512,
    ):
        """
        Initialize the LLM client with API keys and default parameters.

        Args:
            default_together_model: Default Together AI model to use
            temperature: Default temperature for generation
            max_tokens: Default max tokens for generation
        """
        self.default_together_model = default_together_model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def get_env_variable(self, key: str) -> str:
        """Return API key from a .env file."""
        return os.getenv(key) # type: ignore

    def _call_google_ai(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> dict:
        """Make API call to Google AI."""


        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens or self.max_tokens

        url = settings.GOOGLE_ENDPOINT
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temp,
                "maxOutputTokens": max_tok
            }
        }
        params = {"key": settings.GOOGLE_API_KEY}

        response = requests.post(url, headers=headers, json=payload, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        text = data['candidates'][0]['content']['parts'][0]['text']
        cleaned_text = text.strip()
        if cleaned_text.startswith("```json") and cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[7:-3].strip()

        return json.loads(cleaned_text)

    def _call_together_ai(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> dict:
        """Make API call to Together AI."""

        model = model or self.default_together_model
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens or self.max_tokens
        self.together_api_key = settings.TOGETHER_AI_API_KEY
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temp,
            "max_tokens": max_tok
        }

        response = requests.post(settings.TOGETHER_AI_ENDPOINT, headers=headers, json=payload, timeout=15)
        response.raise_for_status()

        data = response.json()
        text = data["choices"][0]["message"]["content"]
        cleaned_text = text.strip()
        if cleaned_text.startswith("```json") and cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[7:-3].strip()
        return json.loads(cleaned_text)


    def generate(
        self,
        prompt: str,
        provider: str = "google",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> dict:
        """
        Generate text using specified provider and parameters.

        Args:
            prompt_template: Either a template string with {variable} placeholders
                           or a PromptTemplate object with template and partial_variables
            variables: Dictionary of variables to substitute (if prompt_template is string)
            provider: LLM provider to use ("google" or "together_ai")
            model: Specific model to use (overrides default)
            temperature: Temperature for generation (overrides default)
            max_tokens: Max tokens for generation (overrides default)

        Returns:
            Generated text response
        """
        if provider.lower() == "google":
            return self._call_google_ai(prompt, model, temperature, max_tokens)
        elif provider.lower() == "together_ai":
            return self._call_together_ai(prompt, model, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'google' or 'together_ai'")

"""ChatGPT integration service."""

from __future__ import annotations

import logging
import os

import openai


logger = logging.getLogger(__name__)


class ChatGPTService:
    """Wrapper for the OpenAI Chat Completion API."""

    @classmethod
    async def ask(cls, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not configured")
            return "ChatGPT is not available."
        openai.api_key = api_key
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:  # noqa: BLE001
            logger.error("ChatGPT request failed: %s", exc)
            return "Unable to fetch response from ChatGPT."

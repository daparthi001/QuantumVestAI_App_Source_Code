# ChatGPT UI Integration Guide

This guide explains how to extend QuantumVestAI with conversational features powered by OpenAI's ChatGPT.

## Overview
The UI can optionally send user questions to the ChatGPT API and display the response directly in the web interface. This enables natural language explanations about predictions and market trends.

## Requirements
- An OpenAI API key (`OPENAI_API_KEY`) available as an environment variable.
- The `openai` Python package.

## Service Implementation
Create a service `ChatGPTService` under `ui/services` that wraps the OpenAI API. The service should expose an async method `ask` which accepts a prompt and returns the assistant's reply. When no API key is provided, the service returns a helpful fallback message instead of raising an error.

```python
# ui/services/chatgpt_service.py
import logging
import os
from typing import Optional

import openai

logger = logging.getLogger(__name__)

class ChatGPTService:
    """Simple wrapper around the OpenAI Chat Completion API."""

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
        except Exception as exc:
            logger.error("ChatGPT request failed: %s", exc)
            return "Unable to fetch response from ChatGPT."
```

## UI Endpoint
Expose a FastAPI endpoint that calls `ChatGPTService.ask` and returns the reply as JSON. A simple example:

```python
@router.post("/chatgpt")
async def chatgpt_endpoint(prompt: str) -> dict[str, str]:
    answer = await ChatGPTService.ask(prompt)
    return {"answer": answer}
```

You can render this through a small form in a template or integrate with the existing React frontend.

## Usage
1. Install dependencies and include `openai` in `ui/requirements.txt`.
2. Set `OPENAI_API_KEY` in the environment before starting the UI.
3. Access the `/chatgpt` endpoint from the browser or front-end component to receive responses.

This modular approach keeps ChatGPT optional while allowing powerful conversational features in the UI.

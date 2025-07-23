import asyncio
import os

from ai_stock_platform.ui.services.chatgpt_service import ChatGPTService


async def run():
    # Ensure API key not set
    os.environ.pop("OPENAI_API_KEY", None)
    result = await ChatGPTService.ask("Hello")
    assert "ChatGPT is not available" in result


def test_chatgpt_no_api_key():
    asyncio.run(run())

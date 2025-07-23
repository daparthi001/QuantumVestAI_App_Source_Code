import asyncio
from aiohttp import web
import pytest

from api.agents import DataFetchAgent, DataAnalysisAgent, DataPipelineManager


@pytest.mark.asyncio
async def test_fetch_agent():
    async def handler(request):
        return web.json_response({"value": 42})

    app = web.Application()
    app.router.add_get("/data", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    agent = DataFetchAgent("test", f"http://localhost:{port}/data")
    data = await agent.fetch()
    assert data["value"] == 42

    await runner.cleanup()


@pytest.mark.asyncio
async def test_pipeline_manager():
    async def handler(request):
        return web.json_response({"number": 3})

    app = web.Application()
    app.router.add_get("/data", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    fetch_agent = DataFetchAgent("fetch", f"http://localhost:{port}/data")
    analysis_agent = DataAnalysisAgent("double", lambda d: d["number"] * 2)

    manager = DataPipelineManager()
    manager.add_fetch_agent(fetch_agent)
    manager.add_analysis_agent(analysis_agent)

    result = await manager.run()
    assert result == [6]

    await runner.cleanup()

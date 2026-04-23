import asyncio
from server.server import Server

async def _async_app():
    server = Server()
    await server.run()

def app():
    """Synchronous entrypoint for package runners.

    This runs the asynchronous server using `asyncio.run`. The project
    entry point in `pyproject.toml` points to `app.app:app`, which
    expects a synchronous callable. Expose a sync `app()` that runs the
    async implementation to avoid un-awaited coroutine warnings.
    """
    asyncio.run(_async_app())


if __name__ == "__main__":
    app()

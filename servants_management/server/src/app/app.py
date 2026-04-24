import asyncio
from server.server import Server

async def async_app():
    server = Server()
    await server.run()

def app():
    asyncio.run(async_app())

if __name__ == "__main__":
    app()

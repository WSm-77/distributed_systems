import sys
import sys, traceback, Ice
import asyncio
from pathlib import Path

from typing import List
from server.evictor import Evictor
from utils.utils import create_logger

logger = create_logger(__name__)

class Server:
    def __init__(self):
        pass

    async def run(self, args: List[str] | None = None):
        logger.info("Starting server.+")

        configFileProperties = Ice.Properties()
        config_path = Path(__file__).parent / "server.conf"
        configFileProperties.load(str(config_path))

        initData = Ice.InitializationData()

        initData.properties = Ice.Properties(sys.argv, configFileProperties)

        loop = asyncio.get_running_loop()
        initData.eventLoopAdapter = Ice.asyncio.EventLoopAdapter(loop)

        async with Ice.Communicator(initData=initData) as communicator:
            adapter = communicator.createObjectAdapter("Adapter")

            logger.info("Registering Evictor for empty category (lazy dedicated servants)")
            evictor = Evictor(adapter, capacity=3)
            adapter.addServantLocator(evictor, "")

            adapter.activate()

            try:
                await communicator.shutdownCompleted()
            except asyncio.CancelledError:
                logger.info("Caught Ctrl+C, shutting down...")

if __name__ == "__main__":
    server = Server()
    asyncio.run(server.run(sys.argv))

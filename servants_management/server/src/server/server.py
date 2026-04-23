import sys
import sys, traceback, Ice
import asyncio
from pathlib import Path

from typing import List
from servants.counter_impl import CounterImpl
from servants.intwrapper_impl import IntWrapperObjectImpl, SharedIntWrapperObjectImpl
from utils.utils import create_logger

logger = create_logger(__name__)

class Server:
    def __init__(self):
        self.counter = CounterImpl()
        # Dedicated servants: separate instances (one per object)
        self.int_wrapper_d1 = IntWrapperObjectImpl()
        self.int_wrapper_d2 = IntWrapperObjectImpl()
        # Shared servant: a single instance serving multiple identities
        self.int_wrapper_shared = SharedIntWrapperObjectImpl()

    async def run(self, args: List[str] | None = None):
        # Load the contents of the server.conf file into a Properties object.
        logger.info("Starting server...")

        configFileProperties = Ice.Properties()
        # Load config file from the package directory so running from a
        # different working directory still finds the file.
        config_path = Path(__file__).parent / "server.conf"
        configFileProperties.load(str(config_path))

        initData = Ice.InitializationData()

        # Create a Properties object from the command line arguments and the config file properties; Ice.* properties and
        # other reserved properties set in the sys.argv command-line arguments override the config file properties.
        initData.properties = Ice.Properties(sys.argv, configFileProperties)

        # Configure the communicator to use asyncio.
        loop = asyncio.get_running_loop()
        initData.eventLoopAdapter = Ice.asyncio.EventLoopAdapter(loop)

        # Create an Ice communicator. We'll use this communicator to create an object adapter.
        # The communicator gets its properties from the properties object.
        async with Ice.Communicator(initData=initData) as communicator:
            # Create an object adapter that listens for incoming requests and dispatches them to servants.
            adapter = communicator.createObjectAdapter("Adapter")

            # Register the Counter servant with the adapter.
            logger.info("Registering Counter servant as identity='counter'")
            adapter.add(self.counter, Ice.Identity(name="counter"))

            # Register dedicated IntWrapper servants (separate instances)
            logger.info("Registering Dedicated IntWrapper servant as identity='IntWrapper1'")
            adapter.add(self.int_wrapper_d1, Ice.Identity(name="IntWrapper1"))
            logger.info("Registering Dedicated IntWrapper servant as identity='IntWrapper2'")
            adapter.add(self.int_wrapper_d2, Ice.Identity(name="IntWrapper2"))

            # Register a shared IntWrapper servant for multiple identities
            logger.info("Registering Shared IntWrapper servant for identities 'IntWrapperShared1' and 'IntWrapperShared2'")
            adapter.add(self.int_wrapper_shared, Ice.Identity(name="IntWrapperShared1"))
            adapter.add(self.int_wrapper_shared, Ice.Identity(name="IntWrapperShared2"))

            # Start dispatching requests.
            adapter.activate()

            # Wait until the communicator is shut down (never happens here) or the user presses Ctrl+C.
            try:
                await communicator.shutdownCompleted()
            except asyncio.CancelledError:
                logger.info("Caught Ctrl+C, shutting down...")



if __name__ == "__main__":
    server = Server()
    asyncio.run(server.run(sys.argv))

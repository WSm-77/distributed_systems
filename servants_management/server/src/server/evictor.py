import Ice
import logging
import time

from servants.intwrapper_impl import IntWrapperObjectImpl
from servants.counter_impl import CounterImpl
from utils.utils import create_logger
from sortedcontainers import SortedDict
from threading import Lock
from typing import Tuple, Dict

logger = create_logger(__name__, level=logging.DEBUG)
class Evictor(Ice.ServantLocator):
    def __init__(self, adapter: Ice.ObjectAdapter, capacity: int = 10):
        self.adapter = adapter
        self.capacity = capacity
        self.creation_time: SortedDict[str, float] = SortedDict()
        self.servants: Dict[str, IntWrapperObjectImpl] = {}
        self.lock = Lock()
        self.shared_intwrapper: IntWrapperObjectImpl | None = None

    def locate(self, current: Ice.Current) -> Tuple[Ice.Object | None, object | None]:
        with self.lock:
            id_name = current.id.name
            op = current.operation
            logger.info(f"ServantLocator.locate() op={op!r} id={id_name!r}")

            if "counter" in id_name:
                logger.info(f"ServerLocator: creating dedicated servant for id={id_name!r}")
                self.servants[id_name] = CounterImpl()
            else:
                logger.info(f"ServantLocator: using shared servant for id={id_name!r}")
                if self.shared_intwrapper is None:
                    logger.info("Instantiating shared IntWrapper servant for non-counter objects")
                    self.shared_intwrapper = IntWrapperObjectImpl()
                self.servants[id_name] = self.shared_intwrapper

            try:
                # Insert into ASM so subsequent calls reuse the same servant.
                self.adapter.add(self.servants[id_name], current.id)
                logger.info(f"Dedicated servant instantiated and added to ASM for id={id_name!r}")
            except Exception:
                logger.exception("Failed to add servant to adapter ASM")

            self.creation_time[id_name] = time.time()

            logger.debug(f"Current servants: {list(self.servants.keys())}, access times: {self.creation_time}")

            if len(self.servants) > self.capacity:
                # Evict least recently used servant (the first one in the sorted dict).
                try:
                    lru_id, _ = self.creation_time.popitem(0)
                    self.servants.pop(lru_id, None)
                    logger.debug(f"Evicting servant for id={lru_id!r} due to capacity limit")
                    self.adapter.remove(current.id)  # Remove from ASM
                except Exception:
                    logger.exception(f"Failed to remove servant for id={lru_id!r} from adapter ASM")

            return self.servants[id_name], None

    def finished(self, current: Ice.Current, servant: Ice.Object, cookie: object | None):
        pass

    def deactivate(self, category: str):
        logger.info(f"ServantLocator.deactivate() category={category!r}")

    def __repr__(self):
        return f"Evictor(servants={list(self.servants.keys())}, capacity={self.capacity})"

__all__ = ["Evictor"]

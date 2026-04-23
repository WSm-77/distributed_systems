import Ice

from servants.intwrapper_impl import IntWrapperObjectImpl
from servants.counter_impl import CounterImpl
from utils.utils import create_logger
from sortedcontainers import SortedDict
from threading import Lock
from typing import Tuple, Dict
import time

logger = create_logger(__name__)

class MetaServant(Ice.Object):
    """Lightweight servant used only to answer Ice meta-operations (ice_isA, ice_ids, ...).

    The important part is that its _ice_ids contains the Slice type id for the business
    interface so that checkedCast/ice_isA can succeed without creating the full servant.
    """

    # will be filled in dynamically when the locator is created
    _ice_ids = ("::Ice::Object",)

class Evictor(Ice.ServantLocator):
    def __init__(self, adapter: Ice.ObjectAdapter, capacity: int = 10):
        self.adapter = adapter
        self.capacity = capacity
        self.access_time: SortedDict[str, float] = SortedDict()
        self.servants: Dict[str, IntWrapperObjectImpl] = {}
        self.lock = Lock()
        self.meta_servant = MetaServant()
        self.shared_intwrapper: IntWrapperObjectImpl | None = None

    def locate(self, current: Ice.Current) -> Tuple[Ice.Object | None, object | None]:
        with self.lock:
            id_name = current.id.name
            op = current.operation
            logger.info(f"ServantLocator.locate() op={op!r} id={id_name!r}")

            # if op.startswith("ice_"):
            #     logger.info(f"ServantLocator: answering meta-op {op!r} for id={id_name!r} with MetaServant")
            #     return self.meta_servant, None

            if "counter" in id_name:
                logger.info(f"ServerLocator: creating Dedicated servant for id={id_name!r}")
                self.servants[id_name] = CounterImpl()
            else:
                logger.info(f"ServantLocator: creating Dedicated servant for id={id_name!r}")
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

            self.access_time[id_name] = time.time()

            return self.servants[id_name], None

    def finished(self, current: Ice.Current, servant: Ice.Object, cookie: object | None):
        # update last access timestamp (useful for eviction later)
        try:
            self.access_time[current.id.name] = time.time()
            logger.debug(f"ServantLocator.finished() updated access time for {current.id.name!r}")
        except Exception:
            logger.exception("Error in finished()")

    def deactivate(self, category: str):
        logger.info(f"ServantLocator.deactivate() category={category!r}")

__all__ = ["Evictor"]

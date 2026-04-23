from __future__ import annotations

import time
from typing import Any, Dict, Tuple

import Ice

from servants.intwrapper_impl import IntWrapperObjectImpl
from utils.utils import create_logger

logger = create_logger(__name__)


class _MetaServant(Ice.Object):
    """Lightweight servant used only to answer Ice meta-operations (ice_isA, ice_ids, ...).

    The important part is that its _ice_ids contains the Slice type id for the business
    interface so that checkedCast/ice_isA can succeed without creating the full servant.
    """

    # will be filled in dynamically when the locator is created
    _ice_ids = ("::Ice::Object",)


class Evictor(Ice.ServantLocator):
    """ServantLocator that lazily creates dedicated servants and inserts them into the ASM.

    Behavior:
    - For Ice meta-operations (operation name starts with "ice_") the locator returns a
      lightweight _MetaServant instance so checkedCast/ice_isA don't create the full servant.
    - For business operations the locator instantiates the real servant, adds it to the adapter's
      Active Servant Map using the incoming identity, logs instantiation, and returns it.
    """

    def __init__(self, adapter: Ice.ObjectAdapter):
        self._adapter = adapter
        # track access times for optional eviction/LRU
        self._access_times: Dict[str, float] = {}
        # meta servant instance (uses the IntWrapperObject type id so ice_isA works)
        try:
            # import type id from generated bindings
            from generated.ServantsManagement.IntWrapperObject import IntWrapperObject

            _MetaServant._ice_ids = ("::Ice::Object", IntWrapperObject.ice_staticId())
        except Exception:
            # fallback: keep only Ice::Object
            logger.exception("Failed to set meta-servant type ids; checkedCast may not work as expected")

        self._meta_servant = _MetaServant()

    def locate(self, current: Ice.Current) -> Tuple[Ice.Object | None, object | None]:
        id_name = current.id.name
        op = current.operation
        logger.info(f"ServantLocator.locate() op={op!r} id={id_name!r}")

        # If the request is for an Ice meta-operation, return the lightweight meta-servant so
        # checkedCast (which issues ice_isA) does not force creation of the real dedicated servant.
        if op.startswith("ice_"):
            logger.info(f"ServantLocator: answering meta-op {op!r} for id={id_name!r} with MetaServant")
            return self._meta_servant, None

        # Business operation: create the dedicated servant and add it to the ASM.
        logger.info(f"ServantLocator: creating Dedicated servant for id={id_name!r}")
        servant = IntWrapperObjectImpl()

        try:
            # Insert into ASM so subsequent calls reuse the same servant.
            self._adapter.add(servant, current.id)
            self._access_times[id_name] = time.time()
            logger.info(f"Dedicated servant instantiated and added to ASM for id={id_name!r}")
        except Exception:
            logger.exception("Failed to add servant to adapter ASM")

        return servant, None

    def finished(self, current: Ice.Current, servant: Ice.Object, cookie: object | None):
        # update last access timestamp (useful for eviction later)
        try:
            self._access_times[current.id.name] = time.time()
            logger.debug(f"ServantLocator.finished() updated access time for {current.id.name!r}")
        except Exception:
            logger.exception("Error in finished()")

    def deactivate(self, category: str):
        logger.info(f"ServantLocator.deactivate() category={category!r}")


__all__ = ["Evictor"]

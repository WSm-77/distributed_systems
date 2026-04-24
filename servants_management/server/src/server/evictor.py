import Ice
import logging
import time
import json
from pathlib import Path

from servants.intwrapper_impl import IntWrapperObjectImpl
from servants.counter_impl import CounterImpl
from utils.utils import create_logger
from threading import Lock
from typing import Tuple, Dict, Optional, Any

logger = create_logger(__name__, level=logging.DEBUG)
class Evictor(Ice.ServantLocator):
    def __init__(self, adapter: Ice.ObjectAdapter, capacity: int = 10):
        self.adapter = adapter
        self.capacity = capacity
        # mapping id_name -> last access timestamp
        self.creation_time: Dict[str, float] = {}
        # mapping id_name -> servant instance (may point to same object for shared servants)
        self.servants: Dict[str, Ice.Object] = {}
        self.lock = Lock()
        # the shared IntWrapper servant (single instance) for non-counter IDs
        self.shared_intwrapper: Optional[IntWrapperObjectImpl] = None
        # directory where evicted servant states are persisted
        self.state_dir: Path = Path(__file__).parent / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _state_path(self, id_name: str) -> Path:
        # sanitize file name
        safe = "".join(c for c in id_name if c.isalnum() or c in ("-", "_"))
        return self.state_dir / f"{safe}.json"

    def _save_state(self, id_name: str, servant: Ice.Object) -> None:
        file_path = self._state_path(id_name)
        data: Dict[str, Any] = {}
        try:
            if isinstance(servant, CounterImpl):
                data = {"servant_type": "counter", "state": {"counter": servant._counter}}
            elif isinstance(servant, IntWrapperObjectImpl):
                # save only the per-id value for the shared servant
                val = servant._values.get(id_name)
                data = {"servant_type": "intwrapper_shared", "state": {"value": val}}
            else:
                logger.warning(f"Unknown servant type for id={id_name!r}; skipping persistence")
                return

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            logger.info(f"Saved state for id={id_name!r} to {file_path}")
        except Exception:
            logger.exception("Failed to save servant state for %s", id_name)

    def _load_state(self, id_name: str) -> Optional[Dict[str, Any]]:
        file_path = self._state_path(id_name)
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception:
            logger.exception("Failed to load state for %s", id_name)
            return None

    def locate(self, current: Ice.Current) -> Tuple[Ice.Object | None, object | None]:
        with self.lock:
            id_name = current.id.name
            op = current.operation
            logger.info(f"ServantLocator.locate() op={op!r} id={id_name!r}")


            # Attempt to restore persisted state if present
            restored = None
            saved = self._load_state(id_name)
            if saved is not None:
                stype = saved.get("servant_type")
                state = saved.get("state", {})
                if stype == "counter":
                    servant = CounterImpl()
                    servant._counter = state.get("counter", 0)
                    restored = servant
                    logger.info(f"Restored Counter servant for id={id_name!r} from disk (counter={servant._counter})")
                elif stype == "intwrapper_dedicated":
                    servant = IntWrapperObjectImpl()
                    servant._value = state.get("value", 0)
                    restored = servant
                    logger.info(f"Restored dedicated IntWrapper servant for id={id_name!r} from disk (value={servant._value})")
                elif stype == "intwrapper_shared":
                    if self.shared_intwrapper is None:
                        self.shared_intwrapper = IntWrapperObjectImpl()
                    # put the per-id value into the shared servant mapping
                    self.shared_intwrapper._values[id_name] = state.get("value", 0)
                    restored = self.shared_intwrapper
                    logger.info(f"Restored shared IntWrapper state for id={id_name!r} from disk (value={self.shared_intwrapper._values[id_name]})")
                # Remove persisted file after successful restore
                try:
                    self._state_path(id_name).unlink()
                except Exception:
                    logger.exception("Failed to remove state file for %s after restore", id_name)

            if restored is not None:
                servant = restored
            else:
                # No persisted state; create new servant(s)
                if "counter" in id_name.lower():
                    logger.info(f"ServantLocator: creating dedicated Counter servant for id={id_name!r}")
                    servant = CounterImpl()
                else:
                    logger.info(f"ServantLocator: using shared IntWrapper servant for id={id_name!r}")
                    if self.shared_intwrapper is None:
                        logger.info("Instantiating shared IntWrapper servant for non-counter objects")
                        self.shared_intwrapper = IntWrapperObjectImpl()
                    servant = self.shared_intwrapper

            try:
                # Insert into ASM so subsequent calls reuse the same servant.
                self.adapter.add(servant, current.id)
                logger.info(f"Servant instantiated and added to ASM for id={id_name!r}")
            except Exception:
                logger.exception("Failed to add servant to adapter ASM for %s", id_name)

            # Track in-memory servant mapping and access time
            self.servants[id_name] = servant
            self.creation_time[id_name] = time.time()

            logger.debug(f"Current servants: {list(self.servants.keys())}, access times: {self.creation_time}")

            # Eviction: if over capacity, evict least recently used by timestamp
            if len(self.servants) > self.capacity:
                try:
                    lru_id = min(self.creation_time, key=self.creation_time.get)
                    lru_servant = self.servants.get(lru_id)
                    if lru_servant is not None:
                        # Persist state for the LRU servant (pay attention to servant type)
                        self._save_state(lru_id, lru_servant)
                    # Remove mappings
                    self.servants.pop(lru_id, None)
                    self.creation_time.pop(lru_id, None)
                    logger.debug(f"Evicting servant for id={lru_id!r} due to capacity limit")
                    # Remove from ASM by identity (use the exact name)
                    try:
                        self.adapter.remove(Ice.Identity(name=lru_id))
                    except Exception:
                        logger.exception(f"Failed to remove servant for id={lru_id!r} from adapter ASM")
                except Exception:
                    logger.exception("Error during eviction process")

            return self.servants[id_name], None

    def finished(self, current: Ice.Current, servant: Ice.Object, cookie: object | None):
        try:
            self.creation_time[current.id.name] = time.time()
            logger.debug(f"ServantLocator.finished() updated access time for {current.id.name!r}")
        except Exception:
            logger.exception("Error in finished()")

    def deactivate(self, category: str):
        logger.info(f"ServantLocator.deactivate() category={category!r}")

    def __repr__(self):
        return f"Evictor(servants={list(self.servants.keys())}, capacity={self.capacity})"


__all__ = ["Evictor"]

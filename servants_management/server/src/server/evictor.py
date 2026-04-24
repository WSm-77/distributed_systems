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
import shutil

logger = create_logger(__name__, level=logging.DEBUG)
class Evictor(Ice.ServantLocator):
    def __init__(self, adapter: Ice.ObjectAdapter, capacity: int = 10):
        self.adapter = adapter
        self.capacity = capacity
        self.creation_time: Dict[str, float] = {}
        self.servants: Dict[str, Ice.Object] = {}
        self.lock = Lock()
        self.shared_intwrapper: Optional[IntWrapperObjectImpl] = None
        self.state_dir: Path = Path(__file__).parent / "state"
        shutil.rmtree(self.state_dir, ignore_errors=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _state_path(self, id_name: str) -> Path:
        save = "".join(c for c in id_name if c.isalnum() or c in ("-", "_"))
        return self.state_dir / f"{save}.json"

    def _save_state(self, id_name: str, servant: Ice.Object) -> None:
        logger.info(f"Saving state for id={id_name!r} before eviction")
        file_path = self._state_path(id_name)
        data: Dict[str, Any] = {}
        try:
            if isinstance(servant, CounterImpl):
                data = {"servant_type": "counter", "state": {"counter": servant._counter}}
            elif isinstance(servant, IntWrapperObjectImpl):
                data = {"servant_type": "intwrapper_shared", "state": {"values": servant._values}}
                self.shared_intwrapper = None
            else:
                logger.warning(f"Unknown servant type for id={id_name!r}; skipping persistence")
                return

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            logger.info(f"Saved state for id={id_name!r} to {file_path}")
        except Exception:
            logger.exception("Failed to save servant state for %s", id_name)

    def _load_state(self, id_name: str) -> Optional[Dict[str, Any]]:
        logger.debug(f"Attempting to load state for id={id_name!r} from disk")
        file_path = self._state_path(id_name)
        logger.debug(f"Looking for state file at {file_path}")
        if not file_path.exists():
            logger.debug(f"State file for id={id_name!r} not found on disk")
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                logger.debug(f"State file for id={id_name!r} found, loading data")
                data = json.load(f)
            return data
        except Exception:
            logger.exception("Failed to load state for %s", id_name)
            return None

    def evict(self) -> None:
        if len(self.servants) > self.capacity:
            try:
                lru_id = min(self.creation_time, key=self.creation_time.get)
                lru_servant = self.servants.get(lru_id)
                if lru_servant is not None:
                    self._save_state(lru_id, lru_servant)
                self.servants.pop(lru_id, None)
                self.creation_time.pop(lru_id, None)
                logger.debug(f"Evicting servant for id={lru_id!r} due to capacity limit")
                try:
                    self.adapter.remove(Ice.Identity(name=lru_id))
                except Exception:
                    logger.exception(f"Failed to remove servant for id={lru_id!r} from adapter ASM")
            except Exception:
                logger.exception("Error during eviction process")

    def register_servant(self, id_name: str, servant: Ice.Object) -> None:
        if id_name not in self.servants:
            self.adapter.add(servant, Ice.Identity(name=id_name))
        self.servants[id_name] = servant
        self.creation_time[id_name] = time.time()
        logger.debug(f"Registered servant for id={id_name!r}, current servants: {list(self.servants.keys())}")

    def locate(self, current: Ice.Current) -> Tuple[Ice.Object | None, object | None]:
        with self.lock:
            id_name = current.id.name
            op = current.operation
            logger.info(f"ServantLocator.locate() op={op!r} id={id_name!r}")

            if "counter" not in id_name.lower():
                id_name = "intwrapper_shared"

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
                elif stype == "intwrapper_shared":
                    servant = IntWrapperObjectImpl()
                    servant._values = state.get("values", {})
                    restored = servant
                    self.shared_intwrapper = servant
                    logger.info(f"Restored shared IntWrapper servant for id={id_name!r} from disk (value={servant._values.get(id_name, {})})")
                try:
                    self._state_path(id_name).unlink()
                except Exception:
                    logger.exception("Failed to remove state file for %s after restore", id_name)

            if restored is not None:
                self.register_servant(id_name, restored)
            else:
                if "counter" in id_name.lower():
                    logger.info(f"ServantLocator: creating dedicated Counter servant for id={id_name!r}")
                    servant = CounterImpl()
                    self.register_servant(id_name, servant)
                else:
                    logger.info(f"ServantLocator: using shared IntWrapper servant for id={id_name!r}")
                    if self.shared_intwrapper is None:
                        logger.info("Instantiating shared IntWrapper servant for non-counter objects")
                        self.shared_intwrapper = IntWrapperObjectImpl()
                    self.register_servant(id_name, self.shared_intwrapper)

            logger.debug(f"Current servants: {list(self.servants.keys())}, access times: {self.creation_time}")

            self.evict()

            return self.servants[id_name], None

    def finished(self, current: Ice.Current, servant: Ice.Object, cookie: object | None):
        pass

    def deactivate(self, category: str):
        logger.info(f"ServantLocator.deactivate() category={category!r}")

    def __repr__(self):
        return f"Evictor(servants={list(self.servants.keys())}, capacity={self.capacity})"


__all__ = ["Evictor"]

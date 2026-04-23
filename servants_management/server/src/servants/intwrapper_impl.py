from __future__ import annotations

from generated.ServantsManagement import IntWrapperObject
from typing import TYPE_CHECKING, Dict
from utils.utils import create_logger

if TYPE_CHECKING:
    from Ice.Current import Current
    from collections.abc import Awaitable

logger = create_logger(__name__)
class IntWrapperObjectImpl(IntWrapperObject):
    """Dedicated servant: one instance per object, keeps its own value."""
    def __init__(self) -> None:
        super().__init__()
        self._values: Dict[str, int] = {}
        logger.info("Instantiated Dedicated IntWrapperObjectImpl")

    def getValue(self, current: Current) -> int | Awaitable[int]:
        logger.info(f"[Dedicated] getValue called for object {current.id.name}, returning {self._value}")
        return self._values[current.id.name]

    def setValue(self, value: int, current: Current) -> None | Awaitable[None]:
        logger.info(f"[Dedicated] setValue called for object {current.id.name}, setting {self._value} to {value}")
        self._values[current.id.name] = value


class SharedIntWrapperObjectImpl(IntWrapperObject):
    """Shared servant: a single instance serves multiple identities but keeps
    per-object state keyed by the identity name (current.id.name)."""
    def __init__(self) -> None:
        super().__init__()
        # mapping: identity name -> value
        self._values: dict[str, int] = {}
        logger.info("Instantiated Shared IntWrapperObjectImpl")

    def _ensure(self, id_name: str) -> None:
        if id_name not in self._values:
            logger.info(f"[Shared] Creating state for object {id_name}")
            self._values[id_name] = 0

    def getValue(self, current: Current) -> int | Awaitable[int]:
        id_name = current.id.name
        self._ensure(id_name)
        val = self._values[id_name]
        logger.info(f"[Shared] getValue called for object {id_name}, returning {val}")
        return val

    def setValue(self, value: int, current: Current) -> None | Awaitable[None]:
        id_name = current.id.name
        self._ensure(id_name)
        logger.info(f"[Shared] setValue called for object {id_name}, setting {self._values[id_name]} to {value}")
        self._values[id_name] = value

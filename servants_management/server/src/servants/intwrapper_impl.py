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
        value = self._values.get(current.id.name, 0)
        logger.info(f"[Dedicated] getValue called for object {current.id.name}, using servant {self}, returning {value}")
        return value

    def setValue(self, value: int, current: Current) -> None | Awaitable[None]:
        logger.info(f"[Dedicated] setValue called for object {current.id.name}, using servant {self}, setting {self._values.get(current.id.name, 0)} to {value}")
        self._values[current.id.name] = value

    def __repr__(self) -> str:
        return f"IntWrapperObjectImpl(id={id(self)})"

from __future__ import annotations

from generated.ServantsManagement import IntWrapperObject
from typing import TYPE_CHECKING
from utils.utils import create_logger

if TYPE_CHECKING:
    from Ice.Current import Current
    from collections.abc import Awaitable

logger = create_logger(__name__)
class IntWrapperObjectImpl(IntWrapperObject):
    def __init__(self) -> None:
        super().__init__()
        self._value = 0

    def getValue(self, current: Current) -> int | Awaitable[int]:
        logger.info(f"getValue called, for object {current.id.name}, returning {self._value}")
        return self._value

    def setValue(self, value: int, current: Current) -> None | Awaitable[None]:
        logger.info(f"setValue called, for object {current.id.name}, setting {self._value} to {value}")
        self._value = value

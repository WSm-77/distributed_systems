from __future__ import annotations

from generated.ServantsManagement.Counter import Counter
from typing import TYPE_CHECKING
from utils.utils import create_logger

if TYPE_CHECKING:
    from Ice.Current import Current
    from collections.abc import Awaitable

logger = create_logger(__name__)

class CounterImpl(Counter):
    def __init__(self) -> None:
        super().__init__()
        self._counter = 0

    def getCounter(self, current: Current) -> int | Awaitable[int]:
        logger.info(f"getValue called, for object {current.id.name}, returning {self._counter}")
        return self._counter

    def incrementCounter(self, current: Current) -> None | Awaitable[None]:
        logger.info(f"getValue called, for object {current.id.name}, returning {self._counter}")
        self._counter += 1

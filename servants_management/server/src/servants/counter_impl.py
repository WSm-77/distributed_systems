from __future__ import annotations

from generated.ServantsManagement.Counter import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Ice.Current import Current
    from collections.abc import Awaitable

class CounterImpl(Counter):
    def __init__(self) -> None:
        super().__init__()
        self._counter = 0

    def getCounter(self, current: Current) -> int | Awaitable[int]:
        return self._counter

    def incrementCounter(self, current: Current) -> None | Awaitable[None]:
        self._counter += 1

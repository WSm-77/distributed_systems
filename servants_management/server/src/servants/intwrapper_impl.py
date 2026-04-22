from __future__ import annotations

from generated.ServantsManagement import IntWrapperObject
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Ice.Current import Current
    from collections.abc import Awaitable

class IntWrapperObjectImpl(IntWrapperObject):
    def __init__(self) -> None:
        super().__init__()
        self._value = 0

    def getValue(self, current: Current) -> int | Awaitable[int]:
        return self._value

    def setValue(self, value: int, current: Current) -> None | Awaitable[None]:
        self._value = value

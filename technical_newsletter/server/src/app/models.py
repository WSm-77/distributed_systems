from __future__ import annotations

import queue
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.generated_bindings import event_pb2


@dataclass(slots=True)
class SubscriberState:
    categories: set[int]
    skill_levels: set[int]
    events: queue.Queue["event_pb2.Event"]
    active: bool = True

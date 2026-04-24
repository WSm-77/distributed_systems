from __future__ import annotations

import logging
import threading
import uuid

from src.app.generated_bindings import event_pb2
from src.app.service import NotificationService


def build_demo_event(index: int) -> event_pb2.Event:
    categories = [
        event_pb2.WORKSHOP,
        event_pb2.CONFERENCE,
        event_pb2.MEETUP,
        event_pb2.HACKATHON,
    ]
    skill_levels = [event_pb2.BEGINNER, event_pb2.INTERMEDIATE, event_pb2.ADVANCED]

    return event_pb2.Event(
        id=str(uuid.uuid4()),
        title=f"Demo event #{index}",
        category=categories[index % len(categories)],
        skill_level=skill_levels[index % len(skill_levels)],
        location=event_pb2.Location(city="Warsaw", country="Poland"),
        date="2026-05-01",
    )


def run_demo_publisher(service: NotificationService, stop_event: threading.Event) -> None:
    event_index = 0
    while not stop_event.is_set():
        service.publish_event(build_demo_event(event_index))
        event_index += 1
        stop_event.wait(5.0)

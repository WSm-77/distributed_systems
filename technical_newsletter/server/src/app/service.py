from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Iterator

import grpc

from src.app.generated_bindings import event_pb2, event_pb2_grpc
from src.app.models import SubscriberState


class NotificationService(event_pb2_grpc.NotificationServiceServicer):
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subscribers: dict[str, SubscriberState] = {}

    def Subscribe(
        self,
        request: event_pb2.SubscriptionRequest,
        context: grpc.ServicerContext,
    ) -> Iterator[event_pb2.Event]:
        state = SubscriberState(
            categories=set(request.categories),
            skill_levels=set(request.skill_level),
            events=queue.Queue(maxsize=100),
        )

        with self._lock:
            self._subscribers[request.client_id] = state

        logging.info("Client subscribed: %s", request.client_id)

        try:
            while context.is_active() and state.active:
                try:
                    event = state.events.get(timeout=1.0)
                except queue.Empty:
                    continue
                yield event
        finally:
            with self._lock:
                existing = self._subscribers.get(request.client_id)
                if existing is state:
                    self._subscribers.pop(request.client_id, None)
            logging.info("Client stream closed: %s", request.client_id)

    def Unsubscribe(
        self,
        request: event_pb2.UnsubscriptionRequest,
        context: grpc.ServicerContext,
    ) -> event_pb2.UnsubscriptionResponse:
        del context
        with self._lock:
            state = self._subscribers.pop(request.client_id, None)

        if state is None:
            return event_pb2.UnsubscriptionResponse(success=False)

        state.active = False
        logging.info("Client unsubscribed: %s", request.client_id)
        return event_pb2.UnsubscriptionResponse(success=True)

    def publish_event(self, event: event_pb2.Event) -> None:
        with self._lock:
            subscribers = list(self._subscribers.values())

        for subscriber in subscribers:
            if not subscriber.active:
                continue
            if subscriber.categories and event.category not in subscriber.categories:
                continue
            if subscriber.skill_levels and event.skill_level not in subscriber.skill_levels:
                continue

            try:
                subscriber.events.put_nowait(event)
            except queue.Full:
                try:
                    subscriber.events.get_nowait()
                except queue.Empty:
                    pass
                subscriber.events.put_nowait(event)

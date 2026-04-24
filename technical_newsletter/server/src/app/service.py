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
            if request.client_id in self._subscribers:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(f"Client ID '{request.client_id}' is already subscribed")
                raise grpc.RpcError("Client ID already subscribed")

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
        request: event_pb2.UnsubscribeRequest,
        context: grpc.ServicerContext,
    ) -> event_pb2.UnsubscribeResponse:
        del context
        with self._lock:
            state = self._subscribers.pop(request.client_id, None)

        if state is None:
            return event_pb2.UnsubscribeResponse(success=False)

        state.active = False
        logging.info("Client unsubscribed: %s", request.client_id)
        return event_pb2.UnsubscribeResponse(success=True)

    def AddSubscriptionFilters(
        self,
        request: event_pb2.AddSubscriptionFiltersRequest,
        context: grpc.ServicerContext,
    ) -> event_pb2.SubscriptionFiltersResponse:
        del context
        logging.info(f"Adding filters for client {request.client_id}: categories={request.categories}, skill_levels={request.skill_level}")
        with self._lock:
            current_state = self._subscribers.get(request.client_id)
            if current_state is None:
                return event_pb2.SubscriptionFiltersResponse(
                    success=False,
                    client_id=request.client_id,
                    message="Client is not subscribed",
                )

            current_state.categories.update(request.categories)
            current_state.skill_levels.update(request.skill_level)

            category_names = [event_pb2.EventType.Name(value) for value in sorted(current_state.categories)]
            skill_level_names = [
                event_pb2.SkillLevel.Name(value) for value in sorted(current_state.skill_levels)
            ]

            return event_pb2.SubscriptionFiltersResponse(
                success=True,
                client_id=request.client_id,
                skill_level=skill_level_names,
                categories=category_names,
                message="Filters added",
            )

    def RemoveSubscriptionFilters(
        self,
        request: event_pb2.RemoveSubscriptionFiltersRequest,
        context: grpc.ServicerContext,
    ) -> event_pb2.SubscriptionFiltersResponse:
        logging.info(f"Removing filters for client {request.client_id}: categories={request.categories}, skill_levels={request.skill_level}")
        del context
        with self._lock:
            current_state = self._subscribers.get(request.client_id)
            if current_state is None:
                return event_pb2.SubscriptionFiltersResponse(
                    success=False,
                    client_id=request.client_id,
                    message="Client is not subscribed",
                )

            current_state.categories.difference_update(request.categories)
            current_state.skill_levels.difference_update(request.skill_level)

            category_names = [event_pb2.EventType.Name(value) for value in sorted(current_state.categories)]
            skill_level_names = [
                event_pb2.SkillLevel.Name(value) for value in sorted(current_state.skill_levels)
            ]

            return event_pb2.SubscriptionFiltersResponse(
                success=True,
                client_id=request.client_id,
                skill_level=skill_level_names,
                categories=category_names,
                message="Filters removed",
            )

    def publish_event(self, event: event_pb2.Event) -> None:
        with self._lock:
            subscribers = list(self._subscribers.values())

        logging.info(f"Publishing event '{event.title}'")
        logging.info(f"Event details: category={event_pb2.EventType.Name(event.category)}, skill_level={event_pb2.SkillLevel.Name(event.skill_level)}")
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

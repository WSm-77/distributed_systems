from __future__ import annotations

import logging
import threading
import time
from concurrent import futures

import grpc

from src.app.generated_bindings import event_pb2_grpc
from src.app.publisher import run_demo_publisher
from src.app.service import NotificationService


def serve() -> None:
    service = NotificationService()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    event_pb2_grpc.add_NotificationServiceServicer_to_server(service, server)
    server.add_insecure_port("[::]:50051")
    server.start()

    stop_event = threading.Event()
    publisher_thread = threading.Thread(
        target=run_demo_publisher,
        args=(service, stop_event),
        daemon=True,
    )
    publisher_thread.start()

    logging.info("gRPC server listening on [::]:50051")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
    finally:
        stop_event.set()
        publisher_thread.join(timeout=2)
        server.stop(grace=3).wait()

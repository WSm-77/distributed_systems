import logging, time, random
from space_agency.shared.models import AdminTopics
from space_agency.utils.utils import create_logger
from space_agency.shared.consumer import Consumer
from space_agency.shared.config import get_settings

class Admin(Consumer):
    def __init__(self, logging_level=logging.DEBUG):
        super().__init__("Admin", logging_level)
        self.logger = create_logger(__name__, logging_level)

    def run(self):
        self.pre_run_configuration()

        settings = get_settings()

        self.channel.queue_declare(
            queue=settings.admin_all_messages_queue,
            durable=True,
            auto_delete=True,
        )

        self.channel.queue_bind(
            exchange=settings.topic_exchange,
            queue=settings.admin_all_messages_queue,
            routing_key="#",
        )

        def callback(ch, method, properties, body):
            self.logger.debug(f"Received message with routing key: {method.routing_key}")
            self.logger.info(body.decode())

        self.consume(
            queue=settings.admin_all_messages_queue,
            on_message_callback=callback,
        )

        try:
            self.start_consuming()
        except KeyboardInterrupt:
            self.stop_consuming()



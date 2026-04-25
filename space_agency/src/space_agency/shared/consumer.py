from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from space_agency.shared.config import get_settings
from space_agency.shared.rabbitmq import setup_infrastructure, get_rabbitmq_connection
from space_agency.utils.utils import create_logger
import logging

class Consumer:
    def __init__(self, name: str, logging_level=logging.DEBUG):
        self.consumer_tags = set()
        self.name = name
        self.logger = create_logger(__name__, logging_level)
        self.connection: BlockingConnection | None = None
        self.channel: BlockingChannel | None = None
        self.settings = get_settings()

    def consume(self, queue: str, on_message_callback):
        self.logger.debug(f"Consumer {self.name} is consuming from {queue}.")
        consumer_tag = self.channel.basic_consume(
            queue=queue,
            on_message_callback=on_message_callback,
            auto_ack=True,
        )
        self.consumer_tags.add(consumer_tag)

    def stop_consuming(self):
        if self.channel and self.channel.is_open:
            self.logger.debug(f"Consumer {self.name} is stopping consuming.")
            for consumer_tag in self.consumer_tags:
                self.channel.stop_consuming(consumer_tag=consumer_tag)
        else:
            self.logger.warning(f"Consumer {self.name} cannot stop consuming because the channel is not open.")

    def pre_run_configuration(self):
        self.connection = get_rabbitmq_connection()
        self.channel = self.connection.channel()
        setup_infrastructure(self.channel)

    def start_consuming(self):
        if self.channel and self.channel.is_open:
            self.logger.debug(f"Consumer {self.name} is starting consuming.")
            self.channel.start_consuming()
        else:
            self.logger.warning(f"Consumer {self.name} cannot start consuming because the channel is not open.")

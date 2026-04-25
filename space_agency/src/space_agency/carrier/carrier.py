from space_agency.shared.models import AdminTopics, Services
from space_agency.shared.consumer import Consumer
from space_agency.shared.callbacks import get_admin_message_callback, get_agency_message_callback
import logging

class Carrier(Consumer):
    def __init__(self, name: str, first_service: Services, second_service: Services, logging_level=logging.DEBUG):
        super().__init__(name, logging_level)
        self.first_service = first_service
        self.second_service = second_service

    def run(self):
        self.logger.info(f"Carrier {self.name} is running.")
        self.logger.info(f"First service: {self.first_service.value}")
        self.logger.info(f"Second service: {self.second_service.value}")

        # Establish a connection to RabbitMQ
        self.pre_run_configuration()

        admin_messages_queue_name = f"{self.settings.carrier_admin_messages_queue}-{self.name}"

        # Declare the queue for receiving admin messages
        self.channel.queue_declare(
            queue=admin_messages_queue_name,
            durable=True,
            auto_delete=True,
        )

        # Bind the queue to the appropriate routing keys
        self.channel.queue_bind(
            exchange=self.settings.topic_exchange,
            queue=admin_messages_queue_name,
            routing_key=AdminTopics.CARRIER.value,
        )

        self.channel.queue_bind(
            exchange=self.settings.topic_exchange,
            queue=admin_messages_queue_name,
            routing_key=AdminTopics.ALL.value,
        )

        agency_message_callback = get_agency_message_callback(self.logger)
        admin_message_callback = get_admin_message_callback(self.logger)

        # Tell RabbitMQ to consume messages from the 'hello' queue
        self.consume(
            queue=self.first_service.value,
            on_message_callback=agency_message_callback,
        )
        self.consume(
            queue=self.second_service.value,
        on_message_callback=agency_message_callback,
        )

        self.consume(
            queue=admin_messages_queue_name,
            on_message_callback=admin_message_callback,
        )

        try:
            self.start_consuming()
        except KeyboardInterrupt:
            self.stop_consuming()

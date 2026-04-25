from space_agency.shared.models import Services
from space_agency.utils.utils import create_logger
from space_agency.shared.consumer import Consumer
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

        # Define a callback function to process incoming messages
        def callback(ch, method, properties, body):
            self.logger.debug(f"Received message with routing key: {method.routing_key}")
            self.logger.info(body.decode())

        # Tell RabbitMQ to consume messages from the 'hello' queue
        self.consume(
            queue=self.first_service.value,
            on_message_callback=callback,
        )
        self.consume(
            queue=self.second_service.value,
            on_message_callback=callback,
        )

        try:
            self.start_consuming()
        except KeyboardInterrupt:
            self.stop_consuming()

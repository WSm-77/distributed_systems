import pika
from space_agency.shared.models import Services
from space_agency.utils.utils import create_logger
from space_agency.shared.rabbitmq import get_rabbitmq_connection
import logging

class Carrier:
    def __init__(self, name: str, first_service: Services, second_service: Services, logging_level=logging.DEBUG):
        self.name = name
        self.first_service = first_service
        self.second_service = second_service
        self.logger = create_logger(__name__, logging_level)

    def run(self):
        self.logger.info(f"Carrier {self.name} is running.")
        self.logger.info(f"First service: {self.first_service.value}")
        self.logger.info(f"Second service: {self.second_service.value}")

        # Establish a connection to RabbitMQ
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        # Declare the queue 'hello' (it needs to exist)
        channel.queue_declare(queue=self.first_service.value, durable=True)
        channel.queue_declare(queue=self.second_service.value, durable=True)

        # Define a callback function to process incoming messages
        def callback(ch, method, properties, body):
            self.logger.debug(f"Received message with routing key: {method.routing_key}")
            self.logger.info(f" [x] Received '{body.decode()}'")

        # Tell RabbitMQ to consume messages from the 'hello' queue
        channel.basic_consume(
            queue=self.first_service.value,
            on_message_callback=callback,
            auto_ack=True
        )
        channel.basic_consume(
            queue=self.second_service.value,
            on_message_callback=callback,
            auto_ack=True
        )

        self.logger.info(' [*] Waiting for messages. To exit press CTRL+C')

        # Start consuming messages (this will block until a message is received)
        channel.start_consuming()

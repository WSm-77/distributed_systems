from space_agency.shared.rabbitmq import get_rabbitmq_connection
from space_agency.shared.models import Services
from space_agency.utils.utils import create_logger
import logging

class Agency:
    def __init__(self, logging_level=logging.DEBUG):
        self.logger = create_logger(__name__, logging_level)

    def run(self):
        # Establish a connection to RabbitMQ
        connection = get_rabbitmq_connection()

        # Declare an exchange (we'll use the default direct exchange here)
        channel = connection.channel()
        channel.exchange_declare(exchange='space-delivery', exchange_type='direct')

        # Declare a queue named 'hello'
        channel.queue_declare(queue=Services.PEOPLE_TRANSPORT.value, durable=True)
        channel.queue_declare(queue=Services.CARGO_TRANSPORT.value, durable=True)
        channel.queue_declare(queue=Services.SATELLITE_DEPLOYMENT.value, durable=True)

        # Bind the queue to the default exchange with a routing key 'hello'
        channel.queue_bind(
            exchange='space-delivery',
            queue=Services.PEOPLE_TRANSPORT.value,
            routing_key=Services.PEOPLE_TRANSPORT.value
        )
        channel.queue_bind(
            exchange='space-delivery',
            queue=Services.CARGO_TRANSPORT.value,
            routing_key=Services.CARGO_TRANSPORT.value
        )
        channel.queue_bind(
            exchange='space-delivery',
            queue=Services.SATELLITE_DEPLOYMENT.value,
            routing_key=Services.SATELLITE_DEPLOYMENT.value
        )

        # The message to send
        message = 'Hello, World!'

        # Publish the message to the exchange with the routing key 'hello'
        # channel.basic_publish(exchange='space-delivery',
                            # routing_key=Services.PEOPLE_TRANSPORT.value,
                            # body=message)
        channel.basic_publish(exchange='space-delivery',
                            routing_key=Services.CARGO_TRANSPORT.value,
                            body=message)

        self.logger.info(f" [x] Sent '{message}'")

        # Close the connection
        connection.close()

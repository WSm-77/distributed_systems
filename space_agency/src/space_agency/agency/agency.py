import time,logging, random, threading
from pika.adapters.blocking_connection import BlockingChannel
from space_agency.shared.callbacks import get_admin_message_callback
from space_agency.shared.models import Services, AdminTopics
from space_agency.utils.utils import create_logger
from space_agency.shared.consumer import Consumer

class Agency(Consumer):
    def __init__(self, name: str = "Agency", logging_level=logging.DEBUG):
        super().__init__(name, logging_level)
        self.logger = create_logger(__name__, logging_level)

    def run(self):
        self.pre_run_configuration()

        # Declare the queue for receiving admin messages
        self.channel.queue_declare(
            queue=self.settings.agency_admin_messages_queue,
            durable=True,
            auto_delete=True,
        )

        # Bind the queue to the appropriate routing keys
        self.channel.queue_bind(
            exchange=self.settings.topic_exchange,
            queue=self.settings.agency_admin_messages_queue,
            routing_key=AdminTopics.AGENCY.value,
        )

        self.channel.queue_bind(
            exchange=self.settings.topic_exchange,
            queue=self.settings.agency_admin_messages_queue,
            routing_key=AdminTopics.ALL.value,
        )

        admin_message_callback = get_admin_message_callback(self.logger)

        self.consume(
            queue=self.settings.agency_admin_messages_queue,
            on_message_callback=admin_message_callback,
        )

        try:
            threading.Thread(
                target=self.generate_jobs,
                daemon=True
            ).start()

            self.start_consuming()
        except KeyboardInterrupt:
            self.stop_consuming()
            self.logger.debug("Agency is shutting down...")

    def generate_jobs(self):
        services = list(Services)

        job_id = 0

        while True:
            service = random.choice(services)
            message = f"""
job: {job_id}
agency: {self.name}
service: {service.value}
time: {time.ctime()}
            """.strip()

            def publish_job():
                self.logger.info(f"Generated job for service: {service.value}")
                self.channel.basic_publish(
                    exchange=self.settings.topic_exchange,
                    routing_key=service.value,
                    body=message
                )
                self.logger.debug(f"Published job with routing key: {service.value}")

            self.connection.add_callback_threadsafe(publish_job)

            job_id += 1
            time.sleep(random.randint(1, 3))

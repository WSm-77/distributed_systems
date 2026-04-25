import time,logging, random, uuid
from pika.adapters.blocking_connection import BlockingChannel
from space_agency.shared.config import get_settings
from space_agency.shared.models import Services, AdminTopics
from space_agency.utils.utils import create_logger
from space_agency.shared.consumer import Consumer

class Agency(Consumer):
    def __init__(self, name: str = "Agency", logging_level=logging.DEBUG):
        super().__init__(name, logging_level)
        self.logger = create_logger(__name__, logging_level)

    def run(self):
        self.pre_run_configuration()

        self.channel.queue_bind(
            exchange=self.settings.topic_exchange,
            queue=self.settings.admin_bradcaset_queue,
            routing_key=AdminTopics.AGENCY.value,
        )

        self.channel.queue_bind(
            exchange=self.settings.topic_exchange,
            queue=self.settings.admin_bradcaset_queue,
            routing_key=AdminTopics.ALL.value,
        )

        try:
            self.generate_jobs(self.channel)
        except KeyboardInterrupt:
            self.logger.debug("Agency is shutting down...")

    def generate_jobs(self, channel: BlockingChannel):
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

            self.logger.info(f"Generated job for service: {service.value}")
            channel.basic_publish(
                exchange=self.settings.topic_exchange,
                routing_key=service.value,
                body=message
            )

            job_id += 1
            time.sleep(random.randint(1, 3))

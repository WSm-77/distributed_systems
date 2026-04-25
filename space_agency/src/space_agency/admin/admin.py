import logging, time, random, threading
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
            threading.Thread(
                target=self.generate_messages,
                daemon=True
            ).start()
            self.start_consuming()
        except KeyboardInterrupt:
            self.stop_consuming()
            self.logger.debug("Admin is shutting down...")


    def generate_messages(self):
        settings = get_settings()

        topics = list(AdminTopics)

        while True:
            topic = random.choice(topics)

            message = f"Admin message at for topic {topic.value} at {time.ctime()}"

            def publish_job():
                self.logger.info(f"Publishing admin message: {message}")
                self.channel.basic_publish(
                    exchange=settings.topic_exchange,
                    routing_key=topic.value,
                    body=message,
                )
                self.logger.debug(f"Published admin message with routing key: {topic.value}")

            self.connection.add_callback_threadsafe(publish_job)
            time.sleep(random.randint(3, 5))

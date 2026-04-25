import pika
from space_agency.shared.config import get_settings
from space_agency.shared.models import Services
from pika.adapters.blocking_connection import BlockingChannel

def get_rabbitmq_connection():
    settings = get_settings()
    connection_parameters = pika.ConnectionParameters(
        settings.rabbitmq_url,
        port=settings.rabbitmq_port,
        credentials=pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_password
        )
    )
    return pika.BlockingConnection(connection_parameters)

def declare_queues(channel: BlockingChannel, queue_names: list[str]):
    for queue_name in queue_names:
        channel.queue_declare(
            queue=queue_name,
            durable=True,
            auto_delete=True,
        )

    # admin broadcast queue
    settings = get_settings()
    channel.queue_declare(
        queue=settings.admin_bradcaset_queue,
        durable=True,
        auto_delete=True,
    )

def bind_queues(channel: BlockingChannel, exchange_name: str, queue_names: list[str]):
    for queue_name in queue_names:
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=queue_name,
        )

def setup_infrastructure(channel: BlockingChannel):
    settings = get_settings()
    channel.exchange_declare(
        exchange=settings.topic_exchange,
        exchange_type='topic',
        durable=True,
        auto_delete=True,
    )

    queue_names = [service.value for service in Services]

    declare_queues(channel, queue_names)
    bind_queues(channel, settings.topic_exchange, queue_names)

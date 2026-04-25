import pika
from space_agency.shared.config import get_settings

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

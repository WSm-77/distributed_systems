import logging

def get_admin_message_callback(logger: logging.Logger):
    def callback(ch, method, properties, body):
        logger.debug(f"Received admin message: {method.routing_key}")
        logger.info(body.decode())
    return callback


def get_agency_message_callback(logger: logging.Logger):
    def callback(ch, method, properties, body):
        logger.debug(f"Received message with routing key: {method.routing_key}")
        logger.info(body.decode())
    return callback

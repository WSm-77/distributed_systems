import logging

def get_admin_message_callback(logger: logging.Logger):
    RESET = "\x1b[0m"
    PURPLE = "\x1b[38;5;93m"
    def callback(ch, method, properties, body):
        logger.debug(f"Received admin message: {method.routing_key}")
        logger.info(f"{PURPLE}[ADMIN MSG]{RESET} {body.decode()}")
    return callback


def get_agency_message_callback(logger: logging.Logger):
    RESET = "\x1b[0m"
    ORAGNE = "\x1b[38;5;208m"
    def callback(ch, method, properties, body):
        logger.debug(f"Received message with routing key: {method.routing_key}")
        logger.info(f"{ORAGNE}[AGENCY MSG]{RESET} {body.decode()}")
    return callback

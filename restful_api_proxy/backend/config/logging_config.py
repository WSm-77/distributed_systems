import logging

import coloredlogs

from config.config import CONFIG


def setup_logging() -> None:
    level = CONFIG.log_level

    root_logger = logging.getLogger()

    if root_logger.handlers:
        root_logger.setLevel(level)
        for handler in root_logger.handlers:
            handler.setLevel(level)
        return

    coloredlogs.install(
        level=level,
        fmt="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s",
    )

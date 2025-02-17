import logging
import os
import sys


def setup_logger():
    logger = logging.getLogger('tavern_bot')

    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level))

    formatter = logging.Formatter('%(asctime)s %(levelname)s\t%(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

logger = setup_logger()
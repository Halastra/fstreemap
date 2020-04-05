"""
LoggingHandler base class
https://stackoverflow.com/a/35177483
"""

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format=r"""%(asctime)-15s %(levelname)-8s %(module)-10s %(name)s:%(funcName)-30s %(message)s"""
)


class LoggingHandler:
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)

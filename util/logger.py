__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

import logging

Logger = logging.getLogger('Bid-Rigging-Detection')

logger_names = ('sqlalchemy.engine.base.Engine')
for logger_name in logger_names:
    _logger = logging.getLogger(logger_name)
    for handler in _logger.handlers:
         Logger.addHandler(handler)

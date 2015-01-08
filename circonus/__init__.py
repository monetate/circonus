from __future__ import absolute_import


__title__ = "circonus"
__version__ = "0.0.0"


from circonus.client import CirconusClient

# Stolen from requests:
# https://github.com/kennethreitz/requests/blob/673bd6afce7ca407c1863be5f6049edd4f5d43b0/requests/__init__.py#L68-L77
import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

"""

circonus.annotation
~~~~~~~~~~~~~~~~~~~

"""

from datetime import datetime
from functools import wraps

from circonus.util import datetime_to_int


class Annotation(object):
    """Construct an :class:`Annotation`.

    :param client: The client to create the annotation with.
    :type client: :class:`CirconusClient`
    :param str title: The title.
    :param str category: The category.
    :param str description: (optional) The description.
    :param list rel_metrics: (optional) The :py:class:`str` names of metrics related to this annotation.

    If ``rel_metrics`` is given, the metric names should be specified in the fully qualified format
    ``<digits>_<string>`` as required by the Circonus API documentation for `annotation
    <https://login.circonus.com/resources/api/calls/annotation>`_.

    """

    RESOURCE_PATH = "annotation"

    def __init__(self, client, title, category, description="", rel_metrics=None):
        self.client = client
        self.title = title
        self.category = category
        self.description = description
        self.rel_metrics = [] if rel_metrics is None else rel_metrics
        self.start = None
        self.stop = None
        self.response = None

    def __call__(self, f):
        """Decorator for creating an annotation around a function or method."""
        @wraps(f)
        def wrapper(*args, **kwargs):
            self.start = datetime.utcnow()
            try:
                r = f(*args, **kwargs)
            finally:
                self.stop = datetime.utcnow()
                self.create()
            return r
        return wrapper

    def __enter__(self):
        self.start = datetime.utcnow()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop = datetime.utcnow()
        self.create()

    def create(self):
        """Create an annotation from the current state."""
        data = {
            "title": self.title,
            "category": self.category,
            "start": datetime_to_int(self.start),
            "stop": datetime_to_int(self.stop),
            "description": self.description,
            "rel_metrics": self.rel_metrics
        }
        self.response = self.client.create(self.RESOURCE_PATH, data)
        return self

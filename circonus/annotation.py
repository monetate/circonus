"""Interact with the Circonus annotation API."""

from calendar import timegm
from datetime import datetime
from functools import wraps


class Annotation(object):
    """Context manager and decorator for creating annotations."""

    RESOURCE_PATH = "annotation"

    @staticmethod
    def datetime_to_int(dt):
        """Convert the given datetime object into an integer."""
        return int(timegm(dt.timetuple()))

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
            "start": self.datetime_to_int(self.start),
            "stop": self.datetime_to_int(self.stop),
            "description": self.description,
            "rel_metrics": self.rel_metrics
        }
        self.response = self.client.create(self.RESOURCE_PATH, data)
        self.response.raise_for_status()
        return self

"""Interact with the Circonus REST API."""

from functools import wraps
from posixpath import sep as pathsep
from urlparse import SplitResult, urlunsplit

import logging
import json

from circonus.tag import with_common_tags
from requests.exceptions import HTTPError

import requests


API_PROTOCOL = "https"
API_LOCATION = "api.circonus.com"
API_VERSION = 2
API_BASE_SPLIT = SplitResult(scheme=API_PROTOCOL, netloc=API_LOCATION, path="/v%d" % API_VERSION, query="", fragment="")
API_BASE_URL = urlunsplit(API_BASE_SPLIT)

log = logging.getLogger(__name__)


def get_api_url(resource_type_or_cid):
    """Get a valid fully qualified API URL for the given resource type or cid string.

    resource type should be specified as "path/to/resource".  cid should be specified as
    "path/to/particular/resource/123456".

    """
    return pathsep.join([API_BASE_URL, resource_type_or_cid.strip(pathsep)])


def log_http_error(f):
    """Decorator to log any HTTPError raised by a request."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            r = f(*args, **kwargs)
            r.raise_for_status()
        except HTTPError as e:
            log.error("%s: %s (%s)", e.response.status_code, e.response.json()["code"],
                      e.response.json()["message"])
        return r
    return wrapper


class CirconusClient(object):
    """A Circonus REST API client."""

    def __init__(self, api_app_name, api_token):
        self.api_app_name = api_app_name
        self.api_token = api_token
        self.api_headers = {
            "Accept": "application/json",
            "X-Circonus-App-Name": self.api_app_name,
            "X-Circonus-Auth-Token": self.api_token
        }

    @log_http_error
    def get(self, resource_type_or_cid, params=None):
        """GET the resource at the given resource type or cid.

        If a cid is given, , e.g., "/check_bundle/123456", a single resource should be returned in the response JSON.
        If a resource type is given, e.g., "/user", a list of resources will be returned in the response JSON.

        """
        return requests.get(get_api_url(resource_type_or_cid), params=params, headers=self.api_headers)

    @log_http_error
    def delete(self, cid, params=None):
        """DELETE the resource at the given cid."""
        return requests.delete(get_api_url(cid), params=params, headers=self.api_headers)

    @with_common_tags
    @log_http_error
    def update(self, cid, data):
        """PUT data to the resource at the given cid.

        data should be a dict.

        """
        return requests.put(get_api_url(cid), data=json.dumps(data), headers=self.api_headers)

    @with_common_tags
    @log_http_error
    def create(self, resource_type, data):
        """POST data to the given resource type.

        data should be a dict.

        """
        return requests.post(get_api_url(resource_type), data=json.dumps(data), headers=self.api_headers)

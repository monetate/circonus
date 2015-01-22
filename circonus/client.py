"""

circonus.client
~~~~~~~~~~~~~~~

"""

from datetime import datetime
from functools import wraps
from posixpath import sep as pathsep
from urlparse import SplitResult, urlunsplit

import logging
import json

from circonus.annotation import Annotation
from circonus.collectd.cpu import get_cpu_graph_data
from circonus.collectd.df import get_df_graph_data
from circonus.collectd.graph import get_collectd_graph_data
from circonus.collectd.memory import get_memory_graph_data
from circonus.collectd.interface import get_interface_graph_data
from circonus.tag import get_tags_with, get_telemetry_tag, is_taggable
from requests import codes as status_codes
from requests.exceptions import HTTPError

import requests


API_PROTOCOL = "https"
API_LOCATION = "api.circonus.com"
API_VERSION = 2
API_BASE_SPLIT = SplitResult(scheme=API_PROTOCOL, netloc=API_LOCATION, path="/v%d" % API_VERSION, query="", fragment="")
API_BASE_URL = urlunsplit(API_BASE_SPLIT)

log = logging.getLogger(__name__)


def get_api_url(resource_type_or_cid):
    """Get a valid fully qualified Circonus API URL for the given resource type or ``cid``.

    :param str resource_type_or_cid: The resource type or ``cid`` representing a specific resource.
    :return: The API URL.
    :rtype: :py:class:`str`

    """
    return pathsep.join([API_BASE_URL, resource_type_or_cid.strip(pathsep)])


def with_common_tags(f):
    """Decorator to ensure that common tags exist on resources.

    Only resources which support tagging via the Circonus API will be affected.

    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        client, cid, data = args[:3]
        common_tags = list(client.common_tags)
        if is_taggable(cid):
            if "type" in data:
                common_tags.append(get_telemetry_tag(data))

            if data.get("tags"):
                updated_tags = get_tags_with(data, common_tags)
                if updated_tags:
                    data.update({"tags": updated_tags})
            else:
                data["tags"] = common_tags
        return f(*args, **kwargs)
    return wrapper


def log_http_error(f):
    """Decorator for :py:mod:`logging` any :class:`~requests.exceptions.HTTPError` raised by a request.

    :raises: :class:`requests.exceptions.HTTPError`

    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            r = f(*args, **kwargs)
            r.raise_for_status()
        except HTTPError as e:
            log.error("%s: %s (%s)", e.response.status_code, e.response.json()["code"],
                      e.response.json()["message"])
            raise
        return r
    return wrapper


class CirconusClient(object):
    """Construct a :class:`CirconusClient`.

    :param str api_app_name: The Circonus API application name.
    :param str api_token: The Circonus API token.
    :param list common_tags: (optional) The :py:class:`str` tags to apply to all resources.
    :rtype: :class:`CirconusClient`

    Usage::

        >>> from circonus import CirconusClient
        >>> circonus = CirconusClient("my-circonus-app", "generated-by-circonus-ui")
        >>> response = circonus.get("/user/current")
        >>> response.json()
        {u'_cid': u'/user/1234',
         u'contact_info': {u'sms': u'', u'xmpp': u''},
         u'email': u'user@example.com',
         u'firstname': u'Ewe',
         u'lastname': u'Sure'}

    """

    def __init__(self, api_app_name, api_token, common_tags=None):
        self.api_app_name = api_app_name
        self.api_token = api_token
        self.api_headers = {
            "Accept": "application/json",
            "X-Circonus-App-Name": self.api_app_name,
            "X-Circonus-Auth-Token": self.api_token
        }
        if common_tags is None:
            self.common_tags = []
        else:
            self.common_tags = common_tags

    @log_http_error
    def get(self, resource_type_or_cid, params=None):
        """Get the resource at resource type or ``cid`` via :func:`requests.get`.

        :param str resource_type_or_cid: The resource type or ``cid`` representing a specific resource.
        :param dict params: (optional) The parameters to pass to :func:`requests.get`.
        :rtype: :class:`requests.Response`

        If a resource type is given, e.g., ``/user``, a :py:class:`list` of resources will exist in the :class:`~requests.Response` JSON.

        If a ``cid`` is given, e.g., ``/check_bundle/123456``, a single resource will exist in the :class:`~requests.Response` JSON.

        """
        return requests.get(get_api_url(resource_type_or_cid), params=params, headers=self.api_headers)

    @log_http_error
    def delete(self, cid, params=None):
        """Delete the resource at ``cid`` via :func:`requests.delete`.

        :param str cid: The resource to delete.
        :param dict params: (optional) The parameters to pass to :func:`requests.delete`.
        :rtype: :class:`requests.Response`

        """
        return requests.delete(get_api_url(cid), params=params, headers=self.api_headers)

    @with_common_tags
    @log_http_error
    def update(self, cid, data):
        """Update the resource at ``cid`` with ``data`` via :func:`requests.put`.

        :param str cid: The resource to update.
        :param dict data: The data used to update the resource.
        :rtype: :class:`requests.Response`

        """
        return requests.put(get_api_url(cid), data=json.dumps(data), headers=self.api_headers)

    @with_common_tags
    @log_http_error
    def create(self, resource_type, data):
        """Create the resource type with ``data`` via :func:`requests.post`.

        :param str resource_type: The resource type to create.
        :param dict data: The data used to create the resource.
        :rtype: :class:`requests.Response`

        """
        return requests.post(get_api_url(resource_type), data=json.dumps(data), headers=self.api_headers)

    def update_with_tags(self, cid, new_tags):
        """Update the resource at ``cid`` to have ``new_tags`` added to it via :func:`update`.

        :param str cid: The resource to update.
        :param list new_tags: The :py:class:`str` tags to add to the resource.
        :rtype: :class:`requests.Response` or :py:const:`False`

        :py:const:`False` is returned in instances where a request to update the resource was not necessary because
        the resource is already tagged with ``new_tags``.

        """
        r = False
        if is_taggable(cid):
            r = self.get(cid)
            tags = get_tags_with(r.json(), new_tags)
            if tags:
                r = self.update(cid, {"tags": tags})
        return r

    def annotation(self, title, category, description="", rel_metrics=None):
        """Context manager and decorator for creating :class:`~circonus.annotation.Annotation` instances.

        :param str title: The title.
        :param str category: The category.
        :param str description: (optional) The description.
        :param list rel_metrics: (optional) The :py:class:`str` names of metrics related to this annotation.
        :rtype: :class:`~circonus.annotation.Annotation`

        If ``rel_metrics`` is given, the metric names should be specified in the fully qualified format
        ``<digits>_<string>`` as required by the Circonus API documentation for `annotation
        <https://login.circonus.com/resources/api/calls/annotation>`_.

        """
        return Annotation(self, title, category, description, rel_metrics)

    def create_annotation(self, title, category, start=None, stop=None, description="", rel_metrics=None):
        """Create an :class:`~circonus.annotation.Annotation` instance immediately.

        :param str title: The title.
        :param str category: The category.
        :param datetime.datetime start: (optional) The start time.
        :param datetime.datetime stop: (optional) The stop time.
        :param str description: (optional) The description.
        :param list rel_metrics: (optional) The :py:class:`str` names of metrics related to this annotation.
        :rtype: :class:`~circonus.annotation.Annotation`

        *Note*: sub-second annotation time resolution is not supported by Circonus.

        ``stop`` defaults to the value of ``start`` if it is not given.

        If ``rel_metrics`` is given, the metric names should be specified in the fully qualified format
        ``<digits>_<string>`` as required by the Circonus API documentation for `annotation
        <https://login.circonus.com/resources/api/calls/annotation>`_.

        """
        a = Annotation(self, title, category, description, rel_metrics)
        a.start = datetime.utcnow() if start is None else start
        a.stop = a.start if stop is None else stop
        a.create()
        return a

    def get_collectd_check_bundle(self, target):
        """Get a ``collectd`` check bundle for ``target``.

        :param str target: The target to filter the check bundle.
        :rtype: :py:class:`dict`

        The *first* ``collectd`` check bundle for ``target`` will be returned.  A given ``target`` should not have
        more than one ``collectd`` check bundle at any given moment.

        """
        r = self.get("check_bundle", {"f_target": target, "f_type": "collectd"})
        check_bundle = r.json()[0]
        return check_bundle

    def create_collectd_cpu_graph(self, target):
        """Create a CPU graph from a ``collectd`` check bundle for ``target``.

        :param str target: The target of the check bundle to filter for.
        :rtype: :class:`requests.Response` or :py:const:`None`

        ``target`` is used to filter ``collectd`` check bundles.

        :py:const:`None` is returned if no data to create the graph could be found for ``target``.

        """
        check_bundle = self.get_collectd_check_bundle(target)
        data = get_cpu_graph_data(check_bundle)
        return self.create("graph", data) if data else None

    def create_collectd_memory_graph(self, target):
        """Create a memory graph from a ``collectd`` check bundle for ``target``.

        :param str target: The target of the check bundle to filter for.
        :rtype: :class:`requests.Response` or :py:const:`None`

        ``target`` is used to filter ``collectd`` check bundles.

        :py:const:`None` is returned if no data to create the graph could be found for ``target``.

        """
        check_bundle = self.get_collectd_check_bundle(target)
        data = get_memory_graph_data(check_bundle)
        return self.create("graph", data) if data else None

    def create_collectd_interface_graph(self, target, interface_name="eth0"):
        """Create an interface graph from a ``collectd`` check bundle for ``target``.

        :param str target: The target of the check bundle to filter for.
        :param str interface_name: (optional) The interface name, e.g., "eth0".
        :rtype: :class:`requests.Response` or :py:const:`None`

        ``target`` is used to filter ``collectd`` check bundles.

        :py:const:`None` is returned if no data to create the graph could be found for ``target``.

        """
        check_bundle = self.get_collectd_check_bundle(target)
        data = get_interface_graph_data(check_bundle, interface_name)
        return self.create("graph", data) if data else None

    def create_collectd_df_graph(self, target, mount_dir):
        """Create a disk free graph from a ``collectd`` check bundle for ``mount_dir`` on ``target``.

        :param str target: The target of the check bundle to filter for.
        :param str mount_dir: The mount directory to create the graph for.
        :rtype: :class:`requests.Response` or :py:const:`None`

        ``target`` is used to filter ``collectd`` check bundles.

        :py:const:`None` is returned if no data to create the graph could be found for ``target``.

        """
        check_bundle = self.get_collectd_check_bundle(target)
        data = get_df_graph_data(check_bundle, mount_dir)
        return self.create("graph", data) if data else None

    def create_collectd_graphs(self, target, interface_names=None, mount_dirs=None):
        """Create several graphs from a ``collectd`` check bundle.

        :param str target: The target of the check bundle to filter for.
        :param list interface_name: (optional) The interface names to create ``interface`` graphs for, e.g., ``["eth0"]``.
        :param list mount_dirs: (optional) The mount directories to create ``df`` graphs for, e.g., ``["/root", "/mnt"]``.
        :rtype: (:py:class:`bool`, :py:class:`list`)

        ``target`` is used to filter ``collectd`` check bundles.

        Only the first ``collectd`` check bundle will be used as no ``target`` should have more than a single
        ``collectd`` check bundle at once.

        ``mount_dirs`` should be a :py:class:`list` of directories where devices are mounted.  ``df`` graphs will be
        created for each.

        ``interface_names`` should be a :py:class:`list` of network interface device names.  ``interface`` graphs will
        be created for each.

        Return :py:const:`True` if all ``collectd`` graphs were created successfully, :py:const:`False` otherwise,
        along with a :py:class:`list` of :class:`requests.Response` instances for requests made.

        """
        if mount_dirs is None:
            mount_dirs = ["root"]

        if interface_names is None:
            interface_names = ["eth0"]

        responses = []
        try:
            check_bundle = self.get_collectd_check_bundle(target)
            graph_data = get_collectd_graph_data(check_bundle, interface_names, mount_dirs)
            for d in graph_data:
                responses.append(self.create("graph", d))
        except HTTPError as e:
            log.error("collectd graphs could not be created: %s", e)

        return responses and all([status_codes.OK == r.status_code for r in responses]), responses

# coding=UTF-8

"""

circonus.collectd.df
~~~~~~~~~~~~~~~~~~~~

Create graph data from a ``collectd`` check bundle containing `df <https://collectd.org/wiki/index.php/Plugin:DF>`_
metrics.

"""

from string import punctuation

import re

from circonus.graph import get_graph_data
from circonus.metric import get_datapoints, get_metrics_sorted_by_suffix
from circonus.util import get_check_id_from_cid


DF_METRIC_SUFFIXES = ["reserved", "used", "free"]
"""Ordered list of metric suffixes.

This list is used to filter and sort metrics in preparation for creating a graph.

"""

DF_METRIC_RE = re.compile(r"""
^df                             # Starts with "df"
`.*                             # Has a mount directory
`df_complex                     # Is a complex metric
`({}|{}|{})$                    # Ends with defined suffix
""".format(*DF_METRIC_SUFFIXES), re.X)
"""A compiled regular expression which matches ``collectd`` metrics."""

PUNCTUATION_TABLE = {ord(c): None for c in punctuation}


def is_mount_dir(metric_name, mount_dir):
    """Is ``metric_name`` the ``collectd`` representation of ``mount_dir``?

    ``collectd`` represents mount directories with ``/`` as ``-``.  This makes it *impossible* to know if a ``-`` in a
    ``collectd`` mount directory was a ``/`` or a ``-`` on the host, e.g., a mount directory may be ``/mnt/solr-home``
    and the metric name representing it may be ``df`mnt-solr-home`df_complex`free``.

    This function takes a naïve approach and removes all punctuation from both directory names before comparing them.

    Both directory names are coerced with :py:func:`unicode` before translation because :mod:`requests` encodes
    responses in UTF-8 by default and Python has different signatures for the function :py:func:`string.translate` and
    the method :py:meth:`str.translate` method.

    """
    split_metric_name = metric_name.split("`")
    if len(split_metric_name) > 1:
        return (unicode(split_metric_name[1]).translate(PUNCTUATION_TABLE) ==
                unicode(mount_dir).translate(PUNCTUATION_TABLE))
    return False


def get_df_metrics(metrics, mount_dir):
    """Get disk free metrics from ``metrics`` for ``mount_dir``.

    :param list metrics: The metrics.
    :param str mount_dir: The mount directory to get metrics for.
    :rtype: :py:class:`list`

    """
    return [m for m in metrics if DF_METRIC_RE.match(m["name"]) and is_mount_dir(m["name"], mount_dir)]


def get_sorted_df_metrics(metrics):
    """Get sorted disk free metrics from ``metrics``.

    :param list metrics: The metrics to sort.
    :rtype: :py:class:`list`

    """
    return get_metrics_sorted_by_suffix(metrics, DF_METRIC_SUFFIXES)


def get_df_datapoints(check_bundle, metrics):
    """Get a list of datapoints from *sorted* ``metrics``.

    :param dict check_bundle: The check bundle.
    :param list metrics: The sorted metrics to cerate datapoints with.
    :rtype: :py:class:`list`

    """
    datapoints = []
    for i, cid in enumerate(check_bundle["_checks"]):
        check_id = get_check_id_from_cid(cid)
        datapoints.extend(get_datapoints(check_id, metrics, {"derive": "gauge", "stack": i}))
    return datapoints


def get_df_graph_data(check_bundle, mount_dir, title=None):
    """Get graph data for ``check_bundle``.

    :param dict check_bundle: The check bundle to create graph data with.
    :param str title: (optional) The title to use for the graph.
    :param str mount_dir: The mount directory to create graph data for.
    :rtype: :py:class:`dict`

    ``title`` defaults to using ``check_bundle["target"]``.  ``df`` and ``mount_dir`` will be appended to ``title``.

    The returned data :py:class:`dict` can be used to :meth:`~circonus.CirconusClient.create` a `graph
    <https://login.circonus.com/resources/api/calls/graph>`_.

    """
    data = {}
    df_metrics = get_df_metrics(check_bundle.get("metrics", []), mount_dir)
    if df_metrics:
        sorted_df_metrics = get_sorted_df_metrics(df_metrics)
        datapoints = get_df_datapoints(check_bundle, sorted_df_metrics)
        graph_title = title if title else "%s df" % check_bundle["target"]
        graph_title = "%s %s" % (graph_title, mount_dir)
        custom_data = {"title": graph_title, "min_left_y": 0, "min_right_y": 0}
        data = get_graph_data(check_bundle, datapoints, custom_data)
    return data

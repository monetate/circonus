"""

circonus.collectd.memory
~~~~~~~~~~~~~~~~~~~~~~~~

"""

import re

from circonus.graph import get_graph_data
from circonus.metric import get_datapoints, get_metrics, get_metrics_sorted_by_suffix
from circonus.util import get_check_id_from_cid


MEMORY_METRIC_SUFFIXES = ["used", "buffered", "cached", "free"]
"""Ordered list of memory metric suffixes.

This list is used to filter and sort memory metrics in preparation for creating a memory graph.

"""

MEMORY_METRIC_RE = re.compile(r"""
^memory                         # Starts with "memory"
`.*`                            # Anything in between
({}|{}|{}|{})$                  # Ends with defined suffix
""".format(*MEMORY_METRIC_SUFFIXES), re.X)
"""A compiled regular expression which matches collectd memory metrics."""


def get_memory_metrics(metrics):
    """Get a sorted list of memory metrics from ``metrics``.

    :param list metrics: The metrics to sort.

    The memory metrics are sorted by explicit suffix, i.e., :const:`~circonus.collectd.memory.MEMORY_METRIC_SUFFIXES`

    """
    return get_metrics_sorted_by_suffix(metrics, MEMORY_METRIC_SUFFIXES)


def get_memory_graph_data(check_bundle):
    """Get memory graph data for ``check_bundle``.

    :param dict check_bundle: The check bundle to create graph data with.
    :rtype: :py:class:`dict`

    The returned data :py:class:`dict` can be used to :meth:`~circonus.CirconusClient.create` a `graph
    <https://login.circonus.com/resources/api/calls/graph>`_.

    """
    metrics = get_memory_metrics(get_metrics(check_bundle, MEMORY_METRIC_RE))
    datapoints = []
    for i, cid in enumerate(check_bundle["_checks"]):
        check_id = get_check_id_from_cid(cid)
        datapoints.extend(get_datapoints(check_id, metrics, {"derive": "gauge", "stack": i}))
    custom_data = {"title": "%s memory" % check_bundle["target"], "min_left_y": 0, "min_right_y": 0}
    return get_graph_data(check_bundle, datapoints, custom_data)

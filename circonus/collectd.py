"""

circonus.collectd
~~~~~~~~~~~~~~~~~

Turn check bundles into graphs and worksheets.

"""

from collections import OrderedDict
from itertools import chain

import re

from circonus.metric import get_metrics_sorted_by_suffix


CPU_METRIC_SUFFIXES = ["steal", "interrupt", "softirq", "system", "wait", "user", "nice", "idle"]
"""Ordered list of CPU metric suffixes.

This list is used to filter and sort CPU metrics in preparation for creating a CPU graph.

"""

CPU_METRIC_RE = re.compile(r"""
^cpu                            # Starts with "cpu"
`.*`                            # Anything in between
""", re.X)
"""A compiled regular expression which matches collectd CPU metrics."""


def get_cpus(metrics):
    """Get a list of strings representing the CPUs available in ``metrics``.

    :param list metrics: The metrics used to look for CPUs.
    :rtype: :py:class:`list`

    The returned strings will begin with the CPU metric name and end with the name identifier.  These strings can be
    used to filter metrics::

        >>> metric["name"].startswith(get_cpus()[0])

    The list is sorted in ascending order.

    """
    cpus = list({m["name"].rpartition("cpu")[0] for m in metrics})
    cpus.sort()
    return cpus


def get_cpu_metrics(metrics):
    """Get a sorted list of CPU metrics from ``metrics``.

    :param list metrics: The metrics to sort.

    The CPU metrics are sorted by:

    #. Name, ascending
    #. Explicit suffix, i.e., :const:`~circonus.collectd.CPU_METRIC_SUFFIXES`

    """
    cpus = get_cpus(metrics)
    cpu_metrics = OrderedDict.fromkeys(cpus)
    for cpu in cpus:
        cpu_metrics[cpu] = get_metrics_sorted_by_suffix((m for m in metrics if m["name"].startswith(cpu)),
                                                        CPU_METRIC_SUFFIXES)
    return list(chain.from_iterable(cpu_metrics.values()))

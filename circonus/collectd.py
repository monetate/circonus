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

CPU_NUMBER_RE = re.compile(r"""
^cpu                            # Starts with "cpu"
`                               # Delimiter
(?P<number>\d+)                 # Number
`                               # Delimiter
""", re.X)
"""A compiled regular expression which captures CPU number from the CPU metric."""

def _get_cpus(metrics):
    """Get a list of strings representing the CPUs available in ``metrics``.

    :param list metrics: The metrics used to look for CPUs.
    :rtype: :py:class:`list`

    The returned strings will begin with the CPU metric name. The list is sorted in ascending order.

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
    cpus = _get_cpus(metrics)
    cpu_metrics = OrderedDict.fromkeys(cpus)
    for cpu in cpus:
        cpu_metrics[cpu] = get_metrics_sorted_by_suffix((m for m in metrics if m["name"].startswith(cpu)),
                                                        CPU_METRIC_SUFFIXES)
    return list(chain.from_iterable(cpu_metrics.values()))


def get_stacked_cpu_metrics(metrics, hide_idle=True):
    """Add a ``stack`` attribute to ``metrics``.

    :param list metrics: The metrics to stack.
    :param bool hide_idle: (optional) Hide CPU idle.

    Each CPU will be added to a stack group equal to that CPU's number.  CPU idle metrics are hidden by default.

    """
    stacked_metrics = list(metrics)
    for m in stacked_metrics:
        match = CPU_NUMBER_RE.match(m["name"])
        m["stack"] = int(match.group("number"))
        if not hide_idle and m["name"].endswith("idle"):
            m["hidden"] = True
    return stacked_metrics

"""

circonus.collectd
~~~~~~~~~~~~~~~~~

Turn check bundles into graphs and worksheets.

"""

import re

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

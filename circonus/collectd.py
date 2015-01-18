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

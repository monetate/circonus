"""

circonus.collectd
~~~~~~~~~~~~~~~~~

Turn check bundles into graphs and worksheets.

"""

import re


CPU_METRIC_RE = re.compile(r"""
^cpu                            # Starts with "cpu"
`.*`                            # Anything in between
""", re.X)
"""A compiled regular expression which matches collectd CPU metrics."""

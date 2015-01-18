"""

circonus.metric
~~~~~~~~~~~~~~~

Manipulate check metrics.

"""

from collections import OrderedDict


def get_unordered_metrics(check_bundle, metric_re):
    """Get an unordered list of metrics from ``check_bundle``.

    :param dict check_bundle: Check bundle of metrics.
    :param re metric_re: Regular expression matching metrics to return.
    :rtype: :py:class:`list`

    """
    return [m for m in check_bundle["metrics"] if metric_re.match(m["name"])]


def get_metrics_sorted_by_suffix(metrics, suffixes):
    """Get a list of metrics sorted by suffix from the list of metrics.

    :param list metrics: Metrics to sort.
    :param list suffixes: Sorted list of suffixes used to sort the return metrics list.
    :rtype: :py:class:`list`

    Sort the ``metrics`` list by metric names ending with values in the ``suffixes`` list.  When creating graphs with
    stacked metrics the order in which metrics are stacked affects the manner in which they are displayed, e.g.,
    perhaps "free" memory makes the most sense when it is at the top of a memory graph.

    """
    metrics_map = OrderedDict.fromkeys(suffixes)
    for m in metrics:
        for s in suffixes:
            if m["name"].endswith(s):
                metrics_map[s] = m
                break
    return metrics_map.values()

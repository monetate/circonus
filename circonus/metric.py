"""

circonus.metric
~~~~~~~~~~~~~~~

Manipulate check metrics.

"""


def get_unordered_metrics(check_bundle, metric_re):
    """Get an unordered list of metrics from ``check_bundle``.

    :param dict check_bundle: Check bundle of metrics.
    :param re metric_re: Regular expression matching metrics to return.
    :rtype: :py:class:`list`

    """
    return [m for m in check_bundle["metrics"] if metric_re.match(m["name"])]

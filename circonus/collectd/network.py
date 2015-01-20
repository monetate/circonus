"""

circonus.collectd.network
~~~~~~~~~~~~~~~~~~~~~~~~~

Create graph data from a ``collectd`` check bundle.

"""


def get_network_metrics(metrics, interface="eth0", kind=None):
    """Get metrics for network ``interface`` and ``kind``.

    :param list metrics: The metrics.
    :param str interface: (optional) The network interface name, e.g., "eth0".
    :param str kind: (optional) The kind of network metrics to get, e.g., "octets".
    :rtype: :py:class:`list`

    """
    if kind:
        network_metrics = [m for m in metrics if m["name"].startswith("interface`%s" % interface) and kind in m["name"]]
    else:
        network_metrics = [m for m in metrics if m["name"].startswith("interface`%s" % interface)]
    network_metrics.sort(reverse=True)
    return network_metrics

"""

circonus.collectd.network
~~~~~~~~~~~~~~~~~~~~~~~~~

Create graph data from a ``collectd`` check bundle.

Transmitted metrics will be on the top of the graph and received metrics will be on the bottom.

"""

from circonus.metric import get_datapoints
from circonus.util import get_check_id_from_cid


DATA_FORMULA_TRANSMITTER = "=8*VAL"
"""The data formula to apply to transmitted network metrics."""

DATA_FORMULA_RECEIVER = "=-8*VAL"
"""The data formula to apply to received network metrics."""


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


def is_transmitter(metric):
    """Is network ``metric`` a transmitter?

    :param dict metric: The metric.
    :rtype: :py:class:`bool`

    """
    return metric.get("name", "").endswith("tx")


def is_receiver(metric):
    """Is network ``metric`` a receiver?

    :param dict metric: The metric.
    :rtype: :py:class:`bool`

    """
    return metric.get("name", "").endswith("rx")


def get_network_datapoints(check_bundle, interface="eth0"):
    """Get a list of datapoints for ``check_bundle`` and ``interface``.

    :param list check_bundle: The check bundle.
    :param str interface: The network interface name, e.g., "eth0".
    :rtype: :py:class:`list`

    """
    datapoints = []
    for cid in check_bundle.get("_checks"):
        check_id = get_check_id_from_cid(cid)
        metrics = check_bundle["metrics"]
        octets = get_network_metrics(metrics, interface, "octets")
        for m in octets:
            if is_transmitter(m):
                m["data_formula"] = DATA_FORMULA_TRANSMITTER
            elif is_receiver(m):
                m["data_formula"] = DATA_FORMULA_RECEIVER
        datapoints.extend(get_datapoints(check_id, octets, {"derive": "counter"}))
        errors = get_network_metrics(metrics, interface, "errors")
        datapoints.extend(get_datapoints(check_id, errors, {"derive": "counter", "axis": "r"}))
    return datapoints

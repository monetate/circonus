"""

circonus.collectd.network
~~~~~~~~~~~~~~~~~~~~~~~~~

Create graph data from a ``collectd`` check bundle.

"""

from circonus.metric import get_datapoints
from circonus.util import get_check_id_from_cid


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
            if m["name"].endswith("tx"):
                m["data_formula"] = "=8*VAL"
            elif m["name"].endswith("rx"):
                m["data_formula"] = "=-8*VAL"
        datapoints.extend(get_datapoints(check_id, octets, {"derive": "counter"}))
        errors = get_network_metrics(metrics, interface, "errors")
        datapoints.extend(get_datapoints(check_id, errors, {"derive": "counter", "axis": "r"}))
    return datapoints

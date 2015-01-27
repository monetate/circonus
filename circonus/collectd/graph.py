"""

circonus.collectd.graph
~~~~~~~~~~~~~~~~~~~~~~~

Create graph data for several ``collectd`` graphs.

"""

from circonus.collectd.cpu import get_cpu_graph_data
from circonus.collectd.df import get_df_graph_data
from circonus.collectd.memory import get_memory_graph_data
from circonus.collectd.interface import get_interface_graph_data


def get_collectd_graph_data(check_bundle, interface_names, mount_dirs, titles=None):
    """Get ``collectd`` graph data for ``check_bundle``.

    :param dict check_bundle: The check bundle to get graph data from.
    :param list interface_names: The interface names to get data for.
    :param list mount_dirs: The mount directories to get data for.
    :param dict titles: (optional) The titles to use for each graph.
    :rtype: :py:class:`list`

    ``titles`` should be a :py:class:`dict` instance mapping a key representing the ``collectd`` plugin name to a
    title for the graph representing it.  For example::

    >>> {"cpu": "test.example.com CPU", "df": "test.example.com Disk"}

    The returned list will only contain valid graph data.

    """
    if titles is None:
        titles = {}

    graph_data = [
        get_cpu_graph_data(check_bundle, title=titles.get("cpu")),
        get_memory_graph_data(check_bundle, title=titles.get("memory"))
    ]
    graph_data.extend([get_interface_graph_data(check_bundle, i,
                                                title=titles.get("interface")) for i in interface_names])
    graph_data.extend([get_df_graph_data(check_bundle, d, title=titles.get("df")) for d in mount_dirs])
    return [d for d in graph_data if d]

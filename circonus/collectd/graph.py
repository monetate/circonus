"""

circonus.collectd.graph
~~~~~~~~~~~~~~~~~~~~~~~

Create graph data for several ``collectd`` graphs.

"""

from circonus.collectd.cpu import get_cpu_graph_data
from circonus.collectd.df import get_df_graph_data
from circonus.collectd.memory import get_memory_graph_data
from circonus.collectd.interface import get_interface_graph_data


def get_collectd_graph_data(check_bundle, interface_names, mount_dirs):
    """Get ``collectd`` graph data for ``check_bundle``.

    :param dict check_bundle: The check bundle to get graph data from.
    :param list interface_names: The interface names to get data for.
    :param list mount_dirs: The mount directories to get data for.
    :rtype: :py:class:`list`

    The returned list will only contain valid graph data.

    """
    graph_data = [
        get_cpu_graph_data(check_bundle),
        get_memory_graph_data(check_bundle)
    ]
    graph_data.extend([get_interface_graph_data(check_bundle, i) for i in interface_names])
    graph_data.extend([get_df_graph_data(check_bundle, d) for d in mount_dirs])
    return [d for d in graph_data if d]

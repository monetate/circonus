"""

circonus.graph
~~~~~~~~~~~~~~

Create graph data from a check bundle.

"""


from circonus.tag import get_tags_with, get_telemetry_tag


def get_graph_data(check_bundle, datapoints, custom_data=None):
    """Get graph data for ``check_bundle`` and  ``datapoints``.

    :param dict check_bundle: The check bundle to create graph data for.
    :param list datapoints: The datapoints to include in the graph data.
    :param dict custom_data: (optional) The custom data to include in the graph data.
    :rtype: :py:class:`dict`

    Merge common graph data with ``custom_data``.  Add the telemetry tag based on the ``type`` attribute of
    ``check_bundle``.

    """
    if custom_data is None:
        custom_data = {"tags": []}
    elif "tags" not in custom_data:
        custom_data["tags"] = []

    tags = get_tags_with(custom_data, [get_telemetry_tag(check_bundle)])
    common = {"datapoints": datapoints}
    if tags:
        common["tags"] = tags

    custom_data.update(common)
    return custom_data

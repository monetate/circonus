"""

circonus.tag
~~~~~~~~~~~~

Manipulate tags on resources that support them.

"""

from circonus.util import get_resource_from_cid


TAGGABLE_RESOURCES = [
    "check_bundle",
    "contact_group",
    "graph",
    "maintenance",
    "metric_cluster",
    "template",
    "worksheet"
]
"""Circonus API resources for which tags can be modified."""


TAG_SEP = ":"


def _get_updated_tags(update_function, *args):
    """Get an updated list of tags.

    :param update_function: The function used to update tags.
    :param args: (The resource :py:class:`dict` to get updated tags for., The tags :py:class:`list` to update ``resource`` with.)
    :rtype: :py:class:`list`

    If the tag list update function modifies the existing tag list then that new list is returned.  In all other cases
    None is returned.

    """
    updated_tags = None
    resource, tags = args[:2]
    existing_tags = resource.get("tags")
    if existing_tags is not None:
        existing_tags_set = set(existing_tags)
        tags_set = set(tags)
        updated_tags_set = update_function(existing_tags_set, tags_set)
        if existing_tags_set != updated_tags_set:
            updated_tags = list(updated_tags_set)
    return updated_tags


def get_tag_string(tag, category=None):
    """Get a string representing ``tag``.

    :param str tag: The tag.
    :param str category: (optional) The category.
    :rtype: :py:class:`str`

    Circonus requires categorized tags to be a string of the form, "category:tag".  Uncategorized tags are simply,
    "tag".

    """
    return TAG_SEP.join([category, tag]) if category else tag


def is_taggable(cid):
    """Is the resource represented by the given cid taggable?

    :param str cid: The ``cid`` of a resource that may support tags.
    :rtype: :py:class:`bool`

    Only resources which support tagging via the Circonus API are considered taggable.  Resources which have a
    ``_tags`` attribute are not considered taggable since the ``_tags`` list cannot be updated via the API -- it is
    read-only.

    """
    return get_resource_from_cid(cid) in TAGGABLE_RESOURCES


def get_tags_with(resource, tags):
    """Get the list of tags for ``resource`` with ``tags`` added to it.

    :param dict resource: The resource with a ``tags`` key.
    :param list tags: The tags to add to ``resource``.
    :rtype: :py:class:`list` or :py:const:`None`

    If ``tags`` changes the existing tags on the resource by adding new tags then that new list of tags is returned.

    If ``tags`` does not change the existing tags on the resource then :py:const:`None` is returned.

    All other failure states resulting from trying to add the list of tags to ``resource`` will return :py:const:`None`.

    """
    return _get_updated_tags(set.union, resource, tags)


def get_tags_without(resource, tags):
    """Get the list of tags for ``resource`` with ``tags`` removed from it.

    :param dict resource: The resource with a ``tags`` key.
    :param list tags: The tags to remove from ``resource``.
    :rtype: :py:class:`list` or :py:const:`None`

    If ``tags`` changes the existing tags on the resource by removing new tags then that new list of tags is returned.

    If ``tags`` does not change the existing tags on the resource then :py:const:`None` is returned.

    All other failure states resulting from trying to remove the list of tags to ``resource`` will return
    :py:const:`None`.

    """
    return _get_updated_tags(set.difference, resource, tags)


def get_telemetry_tag(check_bundle):
    """Get a telemetry tag string for ``check_bundle``.

    :param dict check_bundle: The check bundle to get a telemetry tag from.
    :rtype: :py:class:`str`

    If ``check_bundle`` has a ``type`` attribute, a tag of the form "telemetry:type" will be returned.  This makes
    filtering check bundles by the source of telemetry data easier in the Circonus UI.

    """
    return get_tag_string(check_bundle["type"], "telemetry")

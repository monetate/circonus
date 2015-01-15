"""Interact with the Circonus tag API."""

from circonus.util import get_resource_from_cid


# Circonus API resources for which tags can be modified.
TAGGABLE_RESOURCES = [
    "check_bundle",
    "contact_group",
    "graph",
    "maintenance",
    "metric_cluster",
    "template",
    "worksheet"
]

TAG_SEP = ":"


def _get_tag_string(tag, category=None):
    """Get a string representing the given tag and optional category.

    Circonus requires categorized tags to be a string like, "cat:tag".  Uncategorized tags are simply, "tag".

    """
    return TAG_SEP.join([category, tag]) if category else tag


def _get_updated_tags(update_function, *args):
    """Get an updated list of tags.

    This private function is responsible for abstracting common tag logic.

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


def is_taggable(cid):
    """Is the resource represented by the given cid taggable?

    Only resources which support tagging via the API are considered taggable.  Resources which have a _tags attribute
    are not considered taggable since the _tags list cannot be updated via the API.

    """
    return get_resource_from_cid(cid) in TAGGABLE_RESOURCES


def get_tags_with(resource, tags):
    """Get the list of tags for the given resource with the given list of tags added to it.

    resource should be a dictionary with a "tags" key.  tags should be a list of tags to add to the resource.

    If the given tags list changes the existing list of tags on the resource by adding new tags then that new list of
    tags is returned.

    If the given tags list does not change the existing list of tags on the resource then None is returned.

    All other failure states resulting from trying to add the list of tags to the resource will return None.

    """
    return _get_updated_tags(set.union, resource, tags)


def get_tags_without(resource, tags):
    """Get the list of tags for the given resource with the given lint of tags removed from it.

    resource should be a dictionary with a "tags" key.  tags should be a list of tags to remove from the resource.

    If the given tags list changes the existing list of tags on the resource by removing existing tags then that new
    list of tags is returned.

    If the given tags list does not change the existing list of tags on the resource then None is returned.

    All other failure states resulting from trying to remove the list of tags from the resource will return None.

    """
    return _get_updated_tags(set.difference, resource, tags)


def get_telemetry_tag(check_bundle):
    """Get a telemetry tag string for the given check bundle.

    If the given check bundle has a type attribute a tag of the form, "telemetry:type", will be returned.  This makes
    filtering check bundles by the source of telemetry data easier in the Circonus UI.

    """
    return _get_tag_string(check_bundle["type"], "telemetry")

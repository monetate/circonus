"""Utility functions for interacting with the Circonus REST API."""


from posixpath import sep as pathsep

from colour import Color


def get_check_id_from_cid(cid):
    """Get a check id integer from the given cid string."""
    return int(cid.strip(pathsep).rpartition(pathsep)[-1])


def get_resource_from_cid(cid):
    """Get the resource name from the given cid string."""
    return cid.strip(pathsep).split(pathsep)[0]


def get_colors(items):
    """Get a generator which returns colors for each item in ``items``."""
    if len(items) < 2:
        colors = (c for c in (Color("red"),))
    else:
        color_from = Color("red")
        color_to = Color("green")
        colors = (color_from.range_to(color_to, len(items)))
    return colors

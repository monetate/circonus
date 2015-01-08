"""Utility functions for interacting with the Circonus REST API."""


from posixpath import sep as pathsep


def get_check_id_from_cid(cid):
    """Get a check id integer from the given cid string."""
    return int(cid.strip(pathsep).rpartition(pathsep)[-1])


def get_resource_from_cid(cid):
    """Get the resource name from the given cid string."""
    return cid.strip(pathsep).split(pathsep)[0]

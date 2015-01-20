.. _api:

API
===

.. module:: circonus

The goal of the ``circonus`` package is to combine the ease of use of the
:class:`requests.Response` API with the robust `Circonus REST API`_.

Client Interface
----------------

The majority of functionality is provided by methods belonging to the
:class:`CirconusClient`.  Most methods return a :class:`requests.Response`
object directly.  This gives access to most of the information that
:func:`requests.request` had when the API call was made, along with the
response details.

The `Circonus REST API`_ returns a `JSON`_ encoded response that is available
via the :meth:`requests.Response.json` method on the returned object.  In the
event of an `error`_ the details will available there as well.

.. autoclass:: circonus.CirconusClient
   :members:
   :exclude-members: get, create, update, delete

   .. automethod:: get(resource_type_or_cid, params=None)
   .. automethod:: create(resource_type, data)
   .. automethod:: update(cid, data)
   .. automethod:: delete(cid, params=None)

Client Functions
~~~~~~~~~~~~~~~~

Several functions exist that :class:`CirconusClient` depends on and may be
useful elsewhere:

.. autofunction:: circonus.client.get_api_url
.. autofunction:: circonus.client.with_common_tags
.. autofunction:: circonus.client.log_http_error

Classes
-------

.. autoclass:: circonus.client.Annotation
   :members:

Modules
-------

.. automodule:: circonus.collectd
   :members:

.. automodule:: circonus.collectd.cpu
   :members:

.. automodule:: circonus.collectd.memory
   :members:

.. automodule:: circonus.collectd.network
   :members:

.. automodule:: circonus.graph
   :members:

.. automodule:: circonus.metric
   :members:

.. automodule:: circonus.tag
   :members:

.. automodule:: circonus.util
   :members:

.. _Circonus REST API: https://login.circonus.com/resources/api
.. _JSON: http://json.org/
.. _error: https://login.circonus.com/resources/api#errors

.. _tag:

Tag
===

The :class:`~circonus.CirconusClient` can be setup with a list of
common tags.  These tags will be applied to all resources that are
created via the :meth:`~circonus.CirconusClient.create` method or
updated via the :meth:`~circonus.CirconusClient.update` method.

.. code-block:: python

   COMMON_TAGS = ["category:tag", "global"]
   circonus = CirconusClient(CIRCONUS_API_APP_NAME, CIRCONUS_APP_TOKEN, COMMON_TAGS)

Now when a resource is created:

.. code-block:: python

   response = circonus.create("check_bundle", {
       "brokers": ["/broker/123"],
       "metrics": [{"type": "text", "name":"dummy"}],
       "target": "10.0.0.1",
       "type": "collectd"
   })

It will automatically be tagged with those common tags:

.. code-block:: python

   print response.json()["tags"]
   ["category:tag", "global"]

A few examples for which common tags can be helpful for automatically
tagging resources are:

- The environment, e.g., development, staging, production
- The application layer which created the
  :class:`~circonus.CirconusClient`, e.g., application, database, web
- Platform information, e.g., data center, image name, subnet
- Provisioning information from a configuration management tool

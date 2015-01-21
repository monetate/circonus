Release History
---------------

0.0.10 (2015-10-20)
+++++++++++++++++++

**Improvements**

- Rename ``circonus.collectd.network`` to ``circonus.collectd.interface`` to
  reflect what the name of the ``collectd`` module is.

0.0.9 (2015-01-20)
++++++++++++++++++

**Improvements**

- Add collectd network graph
- Add API documentation

0.0.8 (2015-01-20)
++++++++++++++++++

**Improvements**

- Add collectd memory graph
- Add API documentation

**Bug fixes**

- Fix key error when looking for metrics in a check bundle that has none.
- Handle error state when sorting metrics.  If there were less metrics than
  suffixes to sort by the returned list would contain ``None`` values.  Now an
  empty list is returned.

0.0.7 (2015-01-19)
++++++++++++++++++

**Improvements**

- Add initial support for collectd
- Add graph module
- Add metric module
- Add API documentation

0.0.6 (2015-01-16)
++++++++++++++++++

**Improvements**

- Add optional common tags parameter to CirconusClient class for a cleaner way
  to specify common tags on a given instance of the client.
- Update all docstrings to reStructuredText format with parameter and return
  types.
- Add API documentation.

0.0.5 (2015-01-13)
++++++++++++++++++

**Bug fixes**

- Fix documentation link

0.0.4 (2015-01-13)
++++++++++++++++++

**Improvements**

- Documentation

0.0.3 (2015-01-13)
++++++++++++++++++

**Bug fixes**

- Make the ``with_common_tags`` decorator copy the ``COMMON_TAGS`` list rather
  than modify it.

0.0.2 (2015-01-13)
++++++++++++++++++

**Improvements**

- Annotation decorator, context manager & ad hoc methods
- ``HISTORY.rst``

**Bug fixes**

- Properly unpack ``args`` in ``with_common_tags`` decorator

0.0.1 (2015-01-08)
++++++++++++++++++

- Wrap REST API with requests
- Custom HTTP request headers for app. name and token
- Resource tagging
- Error logging

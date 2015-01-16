circonus
========

Release v\ |version|. (:ref:`Installation <install>`)

``circonus`` is a Python module for interacting with the `Circonus`_ `REST
API`_.

.. code-block:: python

    from circonus import CirconusClient

    CIRCONUS_API_APP_NAME = "my-app"
    CIRCONUS_APP_TOKEN = "generated-by-circonus-ui"

    circonus = CirconusClient(CIRCONUS_API_APP_NAME, CIRCONUS_APP_TOKEN)

A configured ``CirconusClient`` will authenticate via `custom Circonus HTTP
request headers`_ for all subsequent requests:

.. code-block:: python

    response = circonus.get("user/current")
    print response.json()

.. code-block:: python

    {u'_cid': u'/user/1234',
     u'contact_info': {u'sms': u'', u'xmpp': u''},
     u'email': u'user@example.com',
     u'firstname': u'Ewe',
     u'lastname': u'Sure'}

Features
--------

``circonus`` is built on the excellent `requests`_ library.  It extends or
improves the standard `Circonus`_ `REST API`_ by providing several
conveniences and features:

- Application name and token handling
- Resource `tagging`_
- An `annotation`_ decorator and context manager
- `Error`_ logging

User Guide
----------

.. toctree::
   :maxdepth: 2

   user/install
   user/core
   user/annotation
   user/tag

API Documentation
-----------------

.. toctree::
   :maxdepth: 2

   api

.. _Circonus: http://www.circonus.com/
.. _REST API: https://login.circonus.com/resources/api
.. _custom Circonus HTTP request headers: https://login.circonus.com/resources/api#authentication
.. _tagging: https://login.circonus.com/resources/api/calls/tag
.. _requests: http://docs.python-requests.org/en/latest/index.html
.. _Error: https://login.circonus.com/resources/api#errors
.. _annotation: https://login.circonus.com/resources/api/calls/annotation

Circonus
========

A Python module for interacting with the `Circonus`_ `REST API`_.

Features
========

The ``circonus`` package is built on the excellent `requests`_
library.  It extends or improves the standard Circonus REST API by
providing several conveniences and features.

* Application name and token handling
* Resource `tagging`_
* `Error`_ logging

Usage
=====

First, setup the ``CirconusClient``.  Authentication is performed via
`custom Circonus HTTP request headers`_.

.. code-block:: python

    from circonus import CirconusClient


    CIRCONUS_API_APP_NAME = "my-circonus-app"
    CIRCONUS_APP_TOKEN = "generated-in-circonus-ui"
    client = CirconusClient(CIRCONUS_API_APP_NAME, CIRCONUS_APP_TOKEN)

This will set the HTTP request headers for all subsequent requests
made via ``client``:

.. code-block:: python

    print client.api_headers

⏎

.. code-block:: python

    {'Accept': 'application/json',
    'X-Circonus-App-Name': 'my-circonus-app',
    'X-Circonus-Auth-Token': 'generated-in-circonus-ui'}

Get a resource
--------------

The current ``user``:

.. code-block:: python
    r = client.get("user/current")
    r.json()

.. code-block:: python
    r = client.get("user/current")
    r.json()

⏎

.. code-block:: python

    {u'_cid': u'/user/1234',
     u'contact_info': {u'sms': u'', u'xmpp': u''},
     u'email': u'user@example.com',
     u'firstname': u'You',
     u'lastname': u'Sir'}

.. _Circonus: http://www.circonus.com/
.. _REST API: https://login.circonus.com/resources/api
.. _tagging: https://login.circonus.com/resources/api/calls/tag
.. _requests: http://docs.python-requests.org/en/latest/index.html
.. _Error: https://login.circonus.com/resources/api#errors
.. _custom Circonus HTTP request headers: https://login.circonus.com/resources/api#authentication

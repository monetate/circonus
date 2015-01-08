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

===================== ============================
Circonus HTTP header  ``CirconusClient`` parameter
===================== ============================
X-Circonus-App-Name   CIRCONUS_API_APP_NAME
X-Circonus-Auth-Token CIRCONUS_APP_TOKEN
===================== ============================

.. code-block:: python

    from circonus import CirconusClient
    client = CirconusClient(CIRCONUS_API_APP_NAME, CIRCONUS_APP_TOKEN)

Get a resource
--------------

.. code-block:: python
    r = client.get("user/current")
    r.json()

:arrow_right_hook:

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

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

.. code-block:: python

    from circonus import CirconusClient


    client = CirconusClient(CIRCONUS_API_APP_NAME, CIRCONUS_APP_TOKEN)
    r = client.get("user/current")
    r.json()

Should return:

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

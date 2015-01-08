Circonus
========

A Python module for interacting with the `Circonus`_ `REST API`_.

.. image:: https://api.travis-ci.org/monetate/circonus.png?branch=master
   :target: https://travis-ci.org/monetate/circonus
   :alt: Travis CI build status

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

The current `user`_:

.. code-block:: python

    r = client.get("user/current")
    print r.json()

⏎

.. code-block:: python

    {u'_cid': u'/user/1234',
     u'contact_info': {u'sms': u'', u'xmpp': u''},
     u'email': u'user@example.com',
     u'firstname': u'You',
     u'lastname': u'Sir'}

All users:

.. code-block:: python

    r = client.get("user")
    print r.json()

⏎

.. code-block:: python

    [{u'_cid': u'/user/1234',
      u'contact_info': {u'sms': u'', u'xmpp': u''},
      u'email': u'user@example.com',
      u'firstname': u'You',
      u'lastname': u'Sir'},
     {u'_cid': u'/user/1235',
      u'contact_info': {u'sms': u'', u'xmpp': u''},
      u'email': u'umaam@example.com',
      u'firstname': u'You',
      u'lastname': u'Maam'},
      …]

A specific `graph`_:

.. code-block:: python

    r = client.get("graph/6c53484e-b0ad-4652-8b4b-6645fae0db7b")
    print r.json()

⏎

.. code-block:: python

    {u'_cid': u'/graph/6c53484e-b0ad-4652-8b4b-6645fae0db7b',
     u'access_keys': [],
     u'composites': [],
     u'datapoints': […],
     u'description': u'',
     u'guides': [],
     u'line_style': u'stepped',
     u'logarithmic_left_y': None,
     u'logarithmic_right_y': None,
     u'max_left_y': None,
     u'max_right_y': None,
     u'metric_clusters': [],
     u'min_left_y': u'0',
     u'min_right_y': u'0',
     u'notes': None,
     u'style': u'area',
     u'tags': [],
     u'title': u'cpu usage'}

Graphs `filtered`_ by ``title``:

.. code-block:: python

    r = client.get("graph", {"f_title_wildcard": "*cpu*"})
    print r.json()

⏎

.. code-block:: python

    [{u'_cid': u'/graph/6c53484e-b0ad-4652-8b4b-6645fae0db7b',
     u'access_keys': [],
     u'composites': [],
     u'datapoints': […],
     u'description': u'',
     u'guides': [],
     u'line_style': u'stepped',
     u'logarithmic_left_y': None,
     u'logarithmic_right_y': None,
     u'max_left_y': None,
     u'max_right_y': None,
     u'metric_clusters': [],
     u'min_left_y': u'0',
     u'min_right_y': u'0',
     u'notes': None,
     u'style': u'area',
     u'tags': [],
     u'title': u'cpu usage'}]

.. _Circonus: http://www.circonus.com/
.. _REST API: https://login.circonus.com/resources/api
.. _tagging: https://login.circonus.com/resources/api/calls/tag
.. _requests: http://docs.python-requests.org/en/latest/index.html
.. _Error: https://login.circonus.com/resources/api#errors
.. _custom Circonus HTTP request headers: https://login.circonus.com/resources/api#authentication
.. _user: https://login.circonus.com/resources/api/calls/user
.. _graph: https://login.circonus.com/resources/api/calls/graph
.. _filtered: https://login.circonus.com/resources/api#filtering

Circonus
========

A Python module for interacting with the `Circonus`_ `REST API`_.

.. image:: https://pypip.in/v/circonus/badge.png
   :target: https://pypi.python.org/pypi/circonus
   :alt: Latest release

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

Annotation
----------

An `annotation`_ can be created in two ways.  The first is explicitly
via the ``create_annotation`` method:

.. code-block:: python

    annotation = client.create_annotation("title", "category")

Note that the ``create_annotation`` method returns an ``Annotation``
object rather than a ``requests`` response object.  The response
object is available at the ``response`` attribute on the return
object.

The second way to create an annotation is with a decorator or context
manager:

.. code-block:: python

    @client.annotation("title", "category")
    def nap_time():
        sleep(10)

    with client.annotation("title", "category"):
        sleep(10)

These examples will create annotations with the given parameters and
``start`` and ``stop`` times that are automatically set to the UTC
values of the ``__enter__`` and ``__exit__`` magic functions for the
decorated function and context manager, respectively.

.. _Circonus: http://www.circonus.com/
.. _REST API: https://login.circonus.com/resources/api
.. _tagging: https://login.circonus.com/resources/api/calls/tag
.. _requests: http://docs.python-requests.org/en/latest/index.html
.. _Error: https://login.circonus.com/resources/api#errors
.. _custom Circonus HTTP request headers: https://login.circonus.com/resources/api#authentication
.. _user: https://login.circonus.com/resources/api/calls/user
.. _graph: https://login.circonus.com/resources/api/calls/graph
.. _filtered: https://login.circonus.com/resources/api#filtering
.. _annotation: https://login.circonus.com/resources/api/calls/annotation

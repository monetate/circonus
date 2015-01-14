.. _core:

Core
====

Setup the ``CirconusClient``:

.. code-block:: python

    from circonus import CirconusClient

    CIRCONUS_API_APP_NAME = "my-circonus-app"
    CIRCONUS_APP_TOKEN = "generated-by-circonus-ui"

    circonus = CirconusClient(CIRCONUS_API_APP_NAME, CIRCONUS_APP_TOKEN)

Authentication is performed via `custom Circonus HTTP request headers`_.  The
headers are set for all subsequent requests made via the ``circonus`` object:

.. code-block:: python

    print circonus.api_headers

.. code-block:: python

    {'Accept': 'application/json',
    'X-Circonus-App-Name': 'my-circonus-app',
    'X-Circonus-Auth-Token': 'generated-in-circonus-ui'}

Get
---

The current `user`_:

.. code-block:: python

    response = circonus.get("user/current")
    print response.json()

.. code-block:: python

    {u'_cid': u'/user/1234',
     u'contact_info': {u'sms': u'', u'xmpp': u''},
     u'email': u'user@example.com',
     u'firstname': u'Ewe',
     u'lastname': u'Sure'}

All users:

.. code-block:: python

    response = circonus.get("user")
    print response.json()

.. code-block:: python

    [{u'_cid': u'/user/1234',
      u'contact_info': {u'sms': u'', u'xmpp': u''},
      u'email': u'user0@example.com',
      u'firstname': u'Ewe',
      u'lastname': u'Sure'},
     {u'_cid': u'/user/1235',
      u'contact_info': {u'sms': u'', u'xmpp': u''},
      u'email': u'user1@example.com',
      u'firstname': u'Ewe',
      u'lastname': u'Sure Jr.'},
      ...]

A specific `graph`_:

.. code-block:: python

    response = circonus.get("graph/6c53484e-b0ad-4652-8b4b-6645fae0db7b")
    print response.json()

.. code-block:: python

    {u'_cid': u'/graph/6c53484e-b0ad-4652-8b4b-6645fae0db7b',
     u'access_keys': [],
     u'composites': [],
     u'datapoints': [...],
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

    response = circonus.get("graph", {"f_title_wildcard": "*cpu*"})
    print response.json()

.. code-block:: python

    [{u'_cid': u'/graph/6c53484e-b0ad-4652-8b4b-6645fae0db7b',
     u'access_keys': [],
     u'composites': [],
     u'datapoints': [...],
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

Create
------

A `check bundle`_:

.. code-block:: python

    data = {
        "brokers": ["/broker/123"],
        "metrics": [{"type": "text", "name": "dummy"}],
        "target": "10.0.0.1",
        "type": "collectd"
    }
    response = circonus.create("check_bundle", data)
    print response.json()

.. code-block:: python

    {u'_checks': [u'/check/123456'],
     u'_cid': u'/check_bundle/12345',
     u'_created': 1418331830,
     u'_last_modified': 1418331830,
     u'_last_modified_by': u'/user/1234',
     u'brokers': [u'/broker/123'],
     u'config': {u'asynch_metrics': u'false'},
     u'display_name': u'10.0.0.1 - collectd',
     u'metrics': [{u'name': u'dummy', u'status': u'active', u'type': u'text'}],
     u'notes': None,
     u'period': 60,
     u'status': u'active',
     u'tags': [u'telemetry:collectd'],
     u'target': u'10.0.0.1',
     u'timeout': 10,
     u'type': u'collectd'}

.. _custom Circonus HTTP request headers: https://login.circonus.com/resources/api#authentication
.. _user: https://login.circonus.com/resources/api/calls/user
.. _graph: https://login.circonus.com/resources/api/calls/graph
.. _filtered: https://login.circonus.com/resources/api#filtering
.. _check bundle: https://login.circonus.com/resources/api/calls/check_bundle

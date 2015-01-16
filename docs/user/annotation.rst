.. _annotation:

Annotation
==========

A `Circonus annotation
<https://login.circonus.com/resources/api/calls/annotation>`_ can be created
in several ways.

Explicit
--------

.. code-block:: python

    annotation = circonus.create_annotation("title", "category")

*Note:* The :meth:`~circonus.CirconusClient.create_annotation` method returns
an :class:`~circonus.client.Annotation` instance rather than a
:class:`requests.Response` instance.  The :class:`requests.Response` object is
available at the ``response`` attribute on the returned object.

Decorator
---------

.. code-block:: python

    @circonus.annotation("title", "category")
    def nap_time():
        sleep(10)

This will create an annotation with the given parameters and ``start`` and
``stop`` times that are automatically set to the UTC values of the
:py:meth:`object.__enter__` and :py:meth:`object.__exit__` for the decorated
function.

Context Manager
---------------

.. code-block:: python

    with circonus.annotation("title", "category"):
        sleep(10)

This will create an annotation with the given parameters and ``start`` and
``stop`` times that are automatically set to the UTC values of the
:py:meth:`object.__enter__` and :py:meth:`object.__exit__` for the block.

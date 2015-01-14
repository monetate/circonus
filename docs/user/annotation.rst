.. _annotation:

Annotation
==========

An `annotation <https://login.circonus.com/resources/api/calls/annotation>`_
can be created in several ways.

Explicit
--------

.. code-block:: python

    annotation = circonus.create_annotation("title", "category")

*Note:* The ``create_annotation`` method returns an ``Annotation`` object
rather than a ``requests`` response object.  The response object is available
at the ``response`` attribute on the returned object.

Decorator
---------

.. code-block:: python

    @circonus.annotation("title", "category")
    def nap_time():
        sleep(10)

This will create an annotation with the given parameters and ``start`` and
``stop`` times that are automatically set to the UTC values of the `enter`_
and `exit`_ for the decorated function.

Context Manager
---------------

.. code-block:: python

    with circonus.annotation("title", "category"):
        sleep(10)

This will create an annotation with the given parameters and ``start`` and
``stop`` times that are automatically set to the UTC values of the `enter`_
and `exit`_ for the block.

.. _magic methods: http://www.rafekettler.com/magicmethods.html
.. _enter: https://docs.python.org/2/reference/datamodel.html#object.__enter__
.. _exit: https://docs.python.org/2/reference/datamodel.html#object.__exit__

=====
Usage
=====
 
Command Line
------------

.. contents::

git lint [options] [filenames]

Options
-------

.. include:: arguments.rst

As a pre-commit hook:
---------------------

.. code-block:: python

    #!/usr/bin/env python
    import git_lint
    git_lint.run_precommit(staging = True, timestamps = True)

Install this file in your project's ``.git/hooks/pre-commit``, and set
the file's executable flag to ``true``:

.. code-block:: shell

    chmod +x pre-commit

Please see the :ref:`api` for more details on options taken by the
``run_precommit()`` and ``run_gitlint`` commands.

There is an example ``pre-commit`` script shipped with ``git lint``.

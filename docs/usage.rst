=====
Usage
=====

Command Line
------------

.. contents::

git lint [options] [filenames]

Options
-------
``-o`` ``--only``
    A comma-separated list of only those linters to run
``-x`` ``--exclude``
    A comma-separated list of linters to skip
``-l`` ``--linters``
    Show the list of configured linters
``-b`` ``--base``
    Check all changed files in the repository, not just those in the current directory.
``-a`` ``--all``
    Scan all files in the repository, not just those that have changed.
``-e`` ``--every``
    Short for -b -a: scan everything
``-w`` ``--workspace``
    Scan the workspace
``-s`` ``--staging``
    Scan the staging area (useful for pre-commit).
``-g`` ``--changes``
    Report lint failures only for diff'd sections
``-p`` ``--complete``
    Report lint failures for all files
``-c`` ``--config``
    Path to config file
``-d`` ``--dryrun``
    Report what git-lint would do, but don't actually do anything.
``-q`` ``--quiet``
    Produce a short report of files that failed to pass.
``-h`` ``--help``
    This help message
``-v`` ``--version``
    Version information

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
    

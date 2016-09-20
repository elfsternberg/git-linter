=====
Usage
=====

Command Line
------------

.. contents::

git lint [options] [filenames]

Options
-------

``-h`` ``--help``
    Help

``-v`` ``--version``
    Version info

``-c`` ``--config``
    Specify config file (default: ``$GIT_DIR/.git-lint``)

``-w`` ``--workspace``
    Check workspace [default]
    
``-s`` ``--staging``
    Check files in the staging area (useful as a pre-commit hook)
    
``-b`` ``--base``
    Run checks from your repository's root directory. By default,
    ``git-lint`` only runs from the current working directory.

``-a`` ``--all``
    Check all files in repository from the current directory, not
    just changed files

``-e`` ``--everything``
   An alias for ``-b -a``, checks every file in the repository
    
``-o`` ``--only``
    Run only specific linters, skipping all others
    
``-e`` ``--exclude``
    Exclude specific linters, running all others    

As a pre-commit hook:
---------------------

    #!/usr/bin/env python
    import git_lint
    git_lint.run_precommit(staging = True, timestamps = True)

Install this file in your project's ``.git/hooks/pre-commit``, and set
the file's executable flag to ``true``:

    chmod +x pre-commit

Please see the :ref:`api` for more details on options taken by the
``run_precommit()`` and ``run_gitlint`` commands.
    

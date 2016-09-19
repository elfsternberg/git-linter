.. highlight:: shell

============
Installation
============


Stable release
--------------

To install Git Lint, run this command in your terminal:

.. code-block:: console

    $ pip install git_lint

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for Git Lint can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/elfsternberg/git_lint

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/elfsternberg/git_lint/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install

.. _Github repo: https://github.com/elfsternberg/git_lint
.. _tarball: https://github.com/elfsternberg/git_lint/tarball/master

Once installed, you may run the 'git lint --make-config' command, which
will generate a simple configuration file.  You may install this either
in your home directory as ``.git-lint.conf`` or in your project's git
directory as ``.git/lint/git-lint.conf``

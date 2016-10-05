.. highlight:: shell

============
Installation
============


Stable release
--------------

To install Git Lint, run this command in your terminal:

.. code-block:: console

    $ pip install git-linter

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for Git Lint can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/elfsternberg/git-linter

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/elfsternberg/git-linter/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install

.. _Github repo: https://github.com/elfsternberg/git-linter
.. _tarball: https://github.com/elfsternberg/git-linter/tarball/master

Once installed, please copy the '.git-lint' example file.  You may install this either in
your home or repository directory as ``.git-lint``.

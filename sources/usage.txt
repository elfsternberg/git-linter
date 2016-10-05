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

There's a file, pre-commit, in the /bin directory with the project.  (Or you can download
it from the github repository.)  Install it in you .git/hooks/pre-commit file, and
chmod +x .git/hooks/pre-commit.

The pre-commit hook is *experimental*.  Please be careful with it.

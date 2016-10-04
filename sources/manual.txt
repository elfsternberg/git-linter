git-lint(1)
===========

NAME
----
git-lint - Run configured linters against changed files

SYNOPSIS
--------

[verse]
``git lint`` [<options>...] [<files...>]

DESCRIPTION
-----------

Runs a list of configured linters against a specified list of files in
your repository. By default all linters will be run against the
changed files in your current workspace, from the current working
directory on down.  Command line options let you choose a different
directory, a different of files, the complete set of files, and even
the files currently in the staging area.

OPTIONS
-------

.. include:: arguments.rst

OUTPUT
------

By default, the output is that of all the linters specified, in the
order in which they appear in the configuration file, followed by
every file specified, sorted ASCIIbetically.  This order can be
flipped (files first, then linters) with the ``--byfiles`` option.

``git lint`` returns the maximal error code if any linters fail a
pass, or zero if they all succeed.

CONFIGURATION
-------------

``git lint`` uses a standard INI-style configuration file.  Aside from the
DEFAULT section, the name of each section is an alphanumeric token name for
a linter, followed by configuration details for that linter.  Standard details
are:

* output - Text to print before running a linter.
* command - The actual command to run, minus the file path
* match - A comma-separated list of extensions to match against the linter
* print - If true, will prefix each line of output from the linter with the filename
* condition - if "error", the return code of the linter is the status of the pass.  If "output," any output will result in a failure.
* comment - Text to include when running the ``--linters`` option




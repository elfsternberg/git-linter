===============================
Git Lint: README
===============================

A git command that automatically runs identifiable linters against
changed files in your current git repository or staging area.

* Free software: MIT license

**Git Lint** runs a configurable set of syntax, style, and complexity
checkers against changed files in your current working directory or
staging area.  It can be configured to work with any `lint`-like
command.  Some commands may require shell wrappers.

While it may be possible to create a custom lint command in your npm,
grunt, Make, CMake, or whatever, the fact is we all use a VCS, and most
of us use git.  Having a centralized repository for what we want checked
and how we want it checked, associated with git (and by extension, as a
pre-commit hook), that can be run at any time for any reason.

Usage
-----

To lint only what's changed recently in your current working directory:
    `git lint`

To lint everything, changed or otherwise, from the current directory down:
    `git lint -a`

To lint what's changed from the repo's base:
    `git lint -b`

To lint what's in your staging directory:
    `git lint -s`


Documentation
-------------

Complete documentation for the project is available in the docs directory, or at `Git
Linter Docs <https://elfsternberg.github.io/git-linter/index.html>`_.



    
Install
-------

This *ought* to work:

    `pip install git-linter`

You will need to copy the .git-lint configuration file to either your
home directory or the repo`s base directory.  Edit the configuration
file as needed.  You will also need any linters that you plan on
running.

As git-linter is still mostly alpha code, it might be better to install
from source:

    ``
    git clone https://github.com/elfsternberg/git-linter
    python setup.py install
    ``
    


Features
--------

* Highly configurable - configuration files, both for git-lint and
  individual linters, can be global or per-project.

* Only checks files that have been changed, but this can be overriden
  from the command line.

* Can be used directly as a pre-commit hook, to ensure you personally
  don't check in anything broken.

  * Used this way, it checks the *staging* area, not your workspace.

  * When using the staging area, it stashes your current work. Upon
    restoration of your workspace, it ensures the timestamps are the
    same, so as not to confuse your build system or IDE.


Acknowledgements
----------------

`Git lint` started life as a simple pre-commit hook.  Most of the changes since were
inspired by Steve Pulec's `Why You Need a Git Pre-Commit Hook and Why Most Are Wrong <https://dzone.com/articles/why-your-need-git-pre-commit>`_, as well as just my own needs
as a software developer.


Disclaimer
----------

This software, including provided configuration and documentation
materials, is provided "as is" without any warranties, including any
implied warranties of merchantability, fitness, performance, or
quality.  In no event shall the author or sponsor be liable for any
special, direct, indirect, or consequential damages or any damages
whatsoever resulting from loss of use, data or profits, whether in an
action of contract, negligence or other tortious action, arising out
of or in connection with the use or performance of this software.
Each user of the program will agree and understand, and be deemed to
have agreed and understood, that there is no warranty whatsoever for
the program and, accordingly, the entire risk arising from or
otherwise connected with the program is assumed by the user.

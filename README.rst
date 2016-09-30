===============================
Git Lint
===============================

A git command that automatically runs identifiable linters against
changed files in current repository or staging.

* Free software: MIT license

**Git Lint** runs a configurable set of syntax, style, and complexity
checkers against changed files in your current working directory or
staging area.  It can be configured to work with any `lint` command.
Some commands may require shell wrappers.

While it may be possible to create a custom lint command in your npm,
grunt, Make, CMake, or whatever, the fact is we all use a VCS, and
most of us use git.  Having a centralized repository for what we want
checked and how we want it checked, associated with git (and by
extension, as a pre-commit hook), that can be run at any time for any
reason.

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

Credits
-------

The completion of this project was graciously sponsored by my employer,
Splunk <http://splunk.com>.

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

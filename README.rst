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

Features
--------

* Highly configurable - configuration files, both for git-lint and
  individual linters, can be global or per-project.

* Only checks what has been changed, but this can be overriden from the
  command line.

* For some linters, can lint both full-files and or only the parts that
  have changed.

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
implied warranties of merchantability, fitness, performance, or quality.
In no event shall the author or sponsor be liable for any special,
direct, indirect, or consequential damages or any damages whatsoever
resulting from loss of use, data or profits, whether in an action of
contract, negligence or other tortious action, arising out of or in
connection with the use or performance of this software.  Each user of
this program Each user of the program will agree and understand, and be
deemed to have agreed and understood, that there is no warranty
whatsoever for the program and, accordingly, the entire risk arising
from or otherwise connected with the program is assumed by the user.

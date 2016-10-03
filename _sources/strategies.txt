Strategies
----------

git-lint has a couple of phases in which it develops its strategy for what to run:

1. Load the configuration file.
   a. On the command line?
   b. In the base directory as .git-lint?
   c. In the base directory as .git-lint/config?
   d. In the user's home directory as .git-lint?
   e. In the user's home directroy as .git-lint/config?

2. Prune configuration with ``-o`` or ``-e`` options
      
3. Determine which files to lint.
   a.   Workspace or staging?
            i.   If staging, record all stashed timestamps for restoration
   b.   From this list:
            i.   All changed files ``-b``
            ii.  All changed files in the current directory and down (default)
            iii. All files in the current directory and down. ``-a``
            iv.  All files in the repository ``-a -b``
   c.   Add files from command line, if any.
   d.   Filter based on match criteria in configuration file.

4. For each file, run the appropriate linter.
   a.   If in delta mode ``-d``, only show differences that correspond to user changes.
   b.   Capture failure output and failure status.

5.   Reduce failure status to pass/fail
6.   Print resulting messages and exit with failure status (for pre-commit).
7.   If staging, unstage and touch-up files to restore timestamps.

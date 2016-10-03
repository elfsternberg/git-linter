**-o <linters>,  --only=<linters>**
    A comma-separated list of only those linters to run.
**-x <linters> --exclude=<linters>**
    A comma-separated list of linters to skip.
**-l, --linters**
    Show the list of configured linters.
**-b, --base**
    Check all changed files from GIT_DIR, not just those in the current directory and down.
**-a, --all**
    Scan all files, not just those that have changed.
**-e, --every**
    Scan all files, not just those that have changed, from GIT_DIR.  Short for -b -a
**-w, --workspace**
    Scan the workspace [default]
**-s, --staging**
    Scan the staging area (useful for pre-commit).
**-c <path>, --config=<path>**
    Path to config file
**-t, --bylinter**
    Group reports by linter first as they appear in the config file [default]
**-f, --byfile**
    Group reports by file first, linter second
**-d, --dryrun**
    Report what git-lint would do, but don't actually do anything.
**-q, --quiet**
    Produce a short report of file that failed to pass.
**-h, --help**
    Print a short help message
**-V, --verbose**
    Print a slightly more verbose long report
**-v, --version**
    Print version information

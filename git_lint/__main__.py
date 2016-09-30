#!/usr/bin/env python
from __future__ import print_function
from .options import OPTIONS
from .option_handler import cleanup_options
from .reporters import print_report, print_help, print_linters
from .git_lint import load_config, run_linters, git_base
from getopt import GetoptError
import os.path
import sys
import time

watchdog = False
try:
    import watchdog
    from watchdog.observers import Observer
    from watchdog.events import RegexMatchingEventHandler
except Exception as e:
    pass

import gettext
_ = gettext.gettext

NAME = 'git-lint'
VERSION = '0.0.4'


def remove_unavailable_options(options):
    failures = [] + ((watchdog == False and ['monitor']) or [])
    return filter(lambda i: i[1] not in failures, options)


def monitor(options, config, filenames):

    observer = watchdog.observers.Observer()
    skip = ['\.git/']

    def run_monitor_linters():
        (results,
         unlintable_filenames,
         cant_lint_filenames,
         broken_linter_names,
         unfindable_filenames) = run_linters(options, config, filenames)
        
        print_report(results,
                     unlintable_filenames,
                     cant_lint_filenames,
                     broken_linter_names,
                     unfindable_filenames,
                     options)

    class LintMonitor(RegexMatchingEventHandler):
        def __init__(self):
            super(LintMonitor, self).__init__(ignore_regexes=skip)

        def on_created(self, event):
            run_monitor_linters()

        def on_modified(self, event):
            run_monitor_linters()

    observer.schedule(LintMonitor(), git_base, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

            
def main():
    if git_base is None:
        sys.exit(_('A git repository was not found.'))

    initial_options = remove_unavailable_options(OPTIONS)
    (options, filenames, excluded_commands) = cleanup_options(initial_options, sys.argv)

    if len(excluded_commands) > 0:
        print(_('These command line options were ignored due to option precedence.'))
        for exc in excluded_commands:
            print("\t{}".format(exc))

    try:
        config = load_config(options, git_base)

        if 'help' in options:
            print_help(initial_options, NAME)
            return 0

        if 'version' in options:
            from .reporters import print_version
            print_version(NAME, VERSION)
            return 0

        if 'linters' in options:
            from .git_lint import get_linter_status
            working_linter_names, broken_linter_names = get_linter_status(config)
            print_linters(config, broken_linter_names)
            return 0

        if 'monitor' in options:
            return monitor(options, config, filenames)

        (results,
         unlintable_filenames,
         cant_lint_filenames,
         broken_linter_names,
         unfindable_filenames) = run_linters(options, config, filenames)
        
        print_report(results,
                     unlintable_filenames,
                     cant_lint_filenames,
                     broken_linter_names,
                     unfindable_filenames,
                     options)
        
        if not len(results):
            return 0
        
        return max([i[2] for i in results if len(i)])

    except GetoptError as err:
        print_help(initial_options)
        return 1
    

if __name__ == '__main__':
    import sys
    sys.exit(main())

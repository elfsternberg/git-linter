from __future__ import print_function
from functools import reduce
from .git_lint import load_config, run_linters, git_base
import operator
import gettext
_ = gettext.gettext


def print_report(results, unlintable_filenames, cant_lint_filenames,
                 broken_linter_names, unfindable_filenames, options={'bylinter': True}):

    def base_file_cleaner(files):
        return [file.replace(git_base + '/', '', 1) for file in files]

    # ICK.  Mutation, references, and hidden assignment.
    def group_by(iterable, field_id):
        results = []
        keys = {}
        for obj in iterable:
            key = obj[field_id]
            if key in keys:
                keys[key].append(obj)
                continue
            keys[key] = [obj]
            results.append((key, keys[key]))
        return results

    sort_position = 1
    grouping = _('Linter: {}')
    if 'byfile' in options:
        sort_position = 0
        grouping = _('Filename: {}')
    grouped_results = group_by(results, sort_position)

    for group in grouped_results:
        messages = reduce(operator.add, [item[3] for item in group[1]], [])
        if len(messages) == 0:
            continue
        print(grouping.format(group[0]))
        for (filename, lintername, returncode, text) in group[1]:
            if text:
                print('\n'.join(base_file_cleaner(text)))
                print('')
        print ('')

    if len(broken_linter_names) and (len(cant_lint_filenames) or ('verbose' in options)):
        print(_('Linters not found:'), ','.join(broken_linter_names))
        if len(cant_lint_filenames):
            print('  ' + _('Files not linted:'))
            print('\n'.join(['    {}'.format(f) for f in cant_lint_filenames]))
        print('')

    if len(unlintable_filenames) and ('verbose' in options):
        print(_('No recognizeable linters for:'))
        print('\n'.join(['    {}'.format(f) for f in unlintable_filenames]))
        print('')

    if len(unfindable_filenames):
        print(_('Files not found:'))
        print('\n'.join(['    {}'.format(f) for f in unfindable_filenames]))
        print('')

        
def print_help(options, name):
    print(_('Usage: {} [options] [filenames]').format(name))
    for item in options:
        print(' -{:<1}  --{:<12}  {}'.format(item[0], item[1], item[3]))


def print_version(name, version):
    print(_('{} {} Copyright (c) 2009, 2016 Kennth M. "Elf" Sternberg').format(name, version))


def print_linters(config, broken_linter_names):
    print(_('Currently supported linters:'))
    for linter in config:
        print('{:<14} {}'.format(linter.name,
                                 ((linter.name in broken_linter_names and
                                   _('(WARNING: executable not found)') or
                                   linter.linter.get('comment', '')))))



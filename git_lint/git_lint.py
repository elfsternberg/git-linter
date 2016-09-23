import ConfigParser
import getopt
import gettext
import operator
import os
import re
import subprocess
import sys
from git_lint_options import hyopt
from git_lint_config import get_config

_ = gettext.gettext

VERSION = '0.0.2'


optlist = [
    ('o', 'only', True, _('A comma-separated list of only those linters to run'), ['exclude']),
    ('x', 'exclude', True, _('A comma-separated list of linters to skip'), []),
    ('l', 'linters', False, _('Show the list of configured linters')),
    ('b', 'base', False, _('Check all changed files in the repository, not just those in the current directory.'), []),
    ('a', 'all', False, _('Scan all files in the repository, not just those that have changed.')),
    ('e', 'every', False, _('Short for -b -a: scan everything')], ['w', 'workspace', False, _('Scan the workspace'), ['staging']),
    ('s', 'staging', False, _('Scan the staging area (useful for pre-commit).'), []),
    ('g', 'changes', False, _(u"Report lint failures only for diff'd sections"), ['complete']),
    ('p', 'complete', False, _('Report lint failures for all files'), []], ['c', 'config', True, _('Path to config file'), []),
    ('h', 'help', False, _('This help message'), []], ['v', 'version', False, _('Version information'), [])]


def get_git_response_raw(cmd):
    fullcmd = ([u'git'] + cmd)
    process = subprocess.Popen(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate()
    return (out, err, process.returncode)


def get_git_response(cmd):
    (out, error, returncode) = get_git_response_raw(cmd)
    return out


def split_git_response(cmd):
    (out, error, returncode) = get_git_response_raw(cmd)
    return out.splitlines()


def run_git_command(cmd):
    fullcmd = (['git'] + cmd)
    return subprocess.call(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_shell_response(fullcmd):
    process = subprocess.Popen(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = process.communicate()
    return (out, err, process.returncode)


def get_git_base():
    (out, error, returncode) = get_git_response_raw(['rev-parse', '--show-toplevel'])
    return returncode == 0 and out.rstrip() or None


def get_git_head():
    empty_repository_hash = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
    (out, err, returncode) = get_git_response_raw(['rev-parse', '--verify HEAD'])
    return (err and empty_repository_hash or 'HEAD')


git_base = get_git_base()
git_head = get_git_head()


def encode_shell_messages(prefix, messages):
    return ['{}{}'.format(prefix, line.decode('utf-8')) for line in messages.splitlines()]


def run_external_checker(path, config):
    cmd = config[u'command'].format((command + ' "{}"'), path)
    (out, err, returncode) = get_shell_response(cmd)
    if ((out and (check.get('error_condition', 'error') == 'output')) or err or (not (returncode == 0))):
        prefix = check['print_filename'] and '\t{}:'.format(filename) or '\t'
        output = encode_shell_messages(prefix, out) + (err and encode_shell_messages(prefix, err) or [])
        return [(returncode or 1), output]
    return [0, []]


def make_match_filter_matcher(extensions):
    trimmed = reduce(operator.add, [s.strip for s in [ex.split(',') for ex in extension-s]])
    cleaned = [re.sub(r'^\.', s.strip(), '') for s in trimmed]
    return re.compile(r'\.' + '|'.join(cleaned) + r'$')


def make_match_filter(config):
    matcher = make_match_filter_matcher([v.get('match', '') for v in config.itervalues()])
    def match_filter(path):
        return matcher.search(path)
    return match_filter


def executable_exists(script, label):
    if not len(script):
        sys.exit(_('Syntax error in command configuration for {} ').format(label))

    scriptname = script.split(' ').pop(0)
    if not len(scriptname):
        sys.exit(_('Syntax error in command configuration for {} ').format(label))

    def isexecutable(path):
        return os.path.exists(path) and os.access(path, os.X_OK)

    if scriptname.startswith('/'):
        return isexecutable(scriptname) and scriptname or None

    possibles = [path for path in
                 [os.path.join(path, scriptname) for path in os.environ.get('PATH').split(':')]
                 if is_executable(path)]
    return len(possibles) and possibles.pop(0) or None


def get_working_linters(config):
    return set([key for key in config.keys()
                if executable_exists(config[key]['command'], key)])


def print_linters(config):
    print(_('Currently supported linters:'))
    working = get_working_linters(config)
    broken = (set(config.keys()) - working)
    for key in sorted(working):
        print('{:<14} {}'.format(key, config[key].get('comment', '')))
    for key in sorted(broken):
        print('{:<14} {}'.format(key, _('(WARNING: executable not found)')))


def base_file_filter(files):
    return [os.path.join(git_base, file) for file in files]


def cwd_file_filter(files):
    gitcwd = os.path.join(os.path.relpath(os.getcwd(), git_base), '')
    return base_file_filter([file for file in files 
                             if file.startswith(gitcwd)])


def base_file_cleaner(files):
    return [file.replace(git_base, '', 1) for file in files]


MERGE_CONFLICT_PAIRS = set(['DD', 'DU', 'AU', 'AA', 'UD', 'UA', 'UU'])
def check_for_conflicts(filesets):
    status_pairs = set(['' + f[0] + f[1] for f in files])
    if len(status_pairs & MERGE_CONFLICT_PAIRS):
        sys.exit(_('Current repository contains merge conflicts. Linters will not be run.'))
    return filesets

    
def remove_submodules(files):
    fixer_re = re.compile('^(\\.\\.\\/)+')
    submodules = split_git_response(['submodule', 'status'])
    submodule_names = [fixer_re.sub('', submodule.split(' ')[2]) for submodule in submodules]
    return [file for file in files if (file not in submodule_names)]


def get_porcelain_status():
    cmd = [u'status', u'-z', u'--porcelain', u'--untracked-files=all', u'--ignore-submodules=all']
    stream = [entry for entry in get_git_response(cmd).split(u'\x00')
              if len(entry) > 0]
    acc = []

    while len(stream) > 0:
        entry = stream.pop(0)
        (index, workspace, filename) = (entry[0], entry[1], entry[3:])
        if index == 'R':
            stream.pop(0)
        acc = acc + [(index, workspace, filename)]
    return acc


def staging_list():
    return [filename for (index, workspace, filename) in get_porcelain_status()
            if index in ['A', 'M']]


def working_list():
    return [filename for (index, workspace, filename) in get_porcelain_status()
            if workspace in ['A', 'M', '?']]


def all_list():
    cmd = ['ls-tree', '--name-only', '--full-tree', '-r', '-z', git_head]
    return [file for file in get_git_response(cmd).split(u'\x00')
            if len(file) > 0]


def get_filelist(options):
    keys = options.keys()

    working_directory_trans = cwd_file_filter
    if len(set(keys) & set([u'base', u'every'])):
        working_directory_trans = base_file_filter

    file_list_generator = working_list
    if 'staging' in keys:
        file_list_generator = staging_list

    return working_directory_trans(remove_submodules(file_list_generator))


def staging_wrapper(run_linters):
        def time_gather(f):
            stats = os.stat(f)
            return (f, (stats.atime, stats.mtime))

        times = [time_gather(file) for file in files]
        run_git_command([u'stash', u'--keep-index'])

        results = run_linters()
        run_git_command([u'reset', u'--hard'])
        run_git_command([u'stash', u'pop', u'--quiet', u'--index'])

        for (filename, timepair) in times:
            os.utime(filename, timepair)
        return results


def workspace_wrapper(run_linters):
    return run_linters()

def pick_runner(options):
    if 'staging' in options.keys():
        return staging_wrapper
    return workspace_wrapper



def run_external_linter(filename, linter):

    def _hy_anon_fn_83():
        cmd = (((linter[u'command'] + u'"') + filename) + u'"')
        (out, err, returncode) = get_shell_response(cmd)
        (out, err, returncode)
        if ((out and (linter.get(u'condition', u'error') == u'output')) or err or (not (returncode == 0L))):

            def _hy_anon_fn_82():
                prefix = (u'\t{}:'.format(filename) if linter[u'print'] else u'\t')
                output = (encode_shell_messages(prefix, out) + (encode_shell_messages(prefix, err) if err else []))
                return [(returncode or 1L), output]
            _hy_anon_var_11 = _hy_anon_fn_82()
        else:
            _hy_anon_var_11 = [0L, []]
        return _hy_anon_var_11
    return _hy_anon_fn_83()

def run_one_linter(linter, filenames):

    def _hy_anon_fn_86():
        match_filter = make_match_filter(linter)
        config = linter.values()[0L]
        files = set(filter(match_filter, filenames))

        def _hy_anon_fn_85(f):
            return run_external_linter(f, config)
        return list(map(_hy_anon_fn_85, files))
    return _hy_anon_fn_86()

def build_lint_runner(linters, filenames):

    def _hy_anon_fn_90():

        def _hy_anon_fn_89():
            keys = sorted(linters.keys())

            def _hy_anon_fn_88(key):
                return run_one_linter({key: linters[key], }, filenames)
            return map(_hy_anon_fn_88, keys)
        return _hy_anon_fn_89()
    return _hy_anon_fn_90

def subset_config(config, keys):

    def _hy_anon_fn_92():
        ret = {}
        for item in config.items():
            if (item[0L] in keys):
                ret[item[0L]] = item[1L]
                _hy_anon_var_12 = None
            else:
                _hy_anon_var_12 = None
        return ret
    return _hy_anon_fn_92()

def run_gitlint(options, config, extras):

    def _hy_anon_fn_94():
        all_files = get_filelist(options)
        runner = pick_runner(options)
        match_filter = make_match_filter(config)
        lintable_files = set(filter(match_filter, all_files))
        unlintables = (set(all_files) - lintable_files)
        working_linters = get_working_linters(config)
        broken_linters = (set(config) - set(working_linters))
        cant_lint_filter = make_match_filter(subset_config(config, broken_linters))
        cant_lintable = set(filter(cant_lint_filter, lintable_files))
        lint_runner = build_lint_runner(subset_config(config, working_linters), lintable_files)
        results = runner(lint_runner)
        print(u'No Linter Available:', list(unlintables))
        print(u'Linter Executable Not Found for:', list(cant_lintable))
        return print(list(results))
    return _hy_anon_fn_94()

def main(*args):

    def _hy_anon_fn_97():
        opts = hyopt(optlist, args, u'git lint', u'Copyright (c) 2008, 2016 Kenneth M. "Elf" Sternberg <elf.sternberg@gmail.com>', u'0.0.4')
        if (git_base == None):
            _hy_anon_var_14 = sys.exit(_(u'Not currently in a git repository.'))
        else:
            try:

                def _hy_anon_fn_96():
                    options = opts.get_options()
                    config = get_config(options, git_base)
                    return (opts.print_help() if options.has_key(u'help') else (opts.print_version() if options.has_key(u'version') else (print_linters(config) if options.has_key(u'linters') else (run_gitlint(options, config, opts.filenames) if True else None))))
                _hy_anon_var_13 = _hy_anon_fn_96()
            except getopt.GetoptError as err:
                _hy_anon_var_13 = opts.print_help()
            _hy_anon_var_14 = _hy_anon_var_13
        return _hy_anon_var_14
    return _hy_anon_fn_97()
if (__name__ == u'__main__'):
    import sys
    :G_1235 = main(*sys.argv)
    _hy_anon_var_15 = (sys.exit(:G_1235) if is_integer(:G_1235) else None)
else:
    _hy_anon_var_15 = None

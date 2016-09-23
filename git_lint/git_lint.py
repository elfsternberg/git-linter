from hy.core.language import filter, is_integer, map, reduce
import ConfigParser
import os
import subprocess
import operator
import re
import gettext
import sys
import getopt
sys.path.append(u'Users/ksternberg/build/git-lint/git_lint_src')
from git_lint_options import hyopt
from git_lint_config import get_config
_ = gettext.gettext
VERSION = u'0.0.2'

def tap(a):
    print(u'TAP:', a)
    return a
optlist = [[u'o', u'only', True, _(u'A comma-separated list of only those linters to run'), [u'exclude']], [u'x', u'exclude', True, _(u'A comma-separated list of linters to skip'), []], [u'l', u'linters', False, _(u'Show the list of configured linters')], [u'b', u'base', False, _(u'Check all changed files in the repository, not just those in the current directory.'), []], [u'a', u'all', False, _(u'Scan all files in the repository, not just those that have changed.')], [u'e', u'every', False, _(u'Short for -b -a: scan everything')], [u'w', u'workspace', False, _(u'Scan the workspace'), [u'staging']], [u's', u'staging', False, _(u'Scan the staging area (useful for pre-commit).'), []], [u'g', u'changes', False, _(u"Report lint failures only for diff'd sections"), [u'complete']], [u'p', u'complete', False, _(u'Report lint failures for all files'), []], [u'c', u'config', True, _(u'Path to config file'), []], [u'h', u'help', False, _(u'This help message'), []], [u'v', u'version', False, _(u'Version information'), []]]

def get_git_response_raw(cmd):

    def _hy_anon_fn_2():
        fullcmd = ([u'git'] + cmd)
        process = subprocess.Popen(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = process.communicate()
        (out, err)
        return (out, err, process.returncode)
    return _hy_anon_fn_2()

def get_git_response(cmd):

    def _hy_anon_fn_4():
        (out, error, returncode) = get_git_response_raw(cmd)
        (out, error, returncode)
        return out
    return _hy_anon_fn_4()

def split_git_response(cmd):

    def _hy_anon_fn_6():
        (out, error, returncode) = get_git_response_raw(cmd)
        (out, error, returncode)
        return out.splitlines()
    return _hy_anon_fn_6()

def run_git_command(cmd):

    def _hy_anon_fn_8():
        fullcmd = ([u'git'] + cmd)
        return subprocess.call(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return _hy_anon_fn_8()

def get_shell_response(fullcmd):

    def _hy_anon_fn_10():
        process = subprocess.Popen(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = process.communicate()
        (out, err)
        return (out, err, process.returncode)
    return _hy_anon_fn_10()

def _hy_anon_fn_12():
    (out, error, returncode) = get_git_response_raw([u'rev-parse', u'--show-toplevel'])
    (out, error, returncode)
    return (None if (not (returncode == 0L)) else out.rstrip())
git_base = _hy_anon_fn_12()

def _hy_anon_fn_13():
    empty_repository_hash = u'4b825dc642cb6eb9a060e54bf8d69288fbee4904'
    (out, err, returncode) = get_git_response_raw([u'rev-parse', u'--verify HEAD'])
    (out, err, returncode)
    return (u'HEAD' if (not err) else empty_repository_hash)
git_head = _hy_anon_fn_13()

def run_external_checker(path, config):

    def _hy_anon_fn_15():
        cmd = config[u'command'].format((command + u' "{}"'), path)
        (out, err, returncode) = get_shell_response(cmd)
        (out, err, returncode)
        if ((out and (check.get(u'error_condition', u'error') == u'output')) or err or (not (returncode == 0L))):

            def _hy_anon_fn_14():
                prefix = (u'\t{}:'.format(filename) if check[u'print_filename'] else u'\t')
                output = (encode_shell_messages(prefix, out) + (encode_shell_messages(prefix, err) if err else []))
                return [(returncode or 1L), output]
            _hy_anon_var_1 = _hy_anon_fn_14()
        else:
            _hy_anon_var_1 = [0L, []]
        return _hy_anon_var_1
    return _hy_anon_fn_15()

def make_match_filter_matcher(extensions):

    def _hy_anon_fn_17(s):
        return re.compile(s, re.I)

    def _hy_anon_fn_18(s):
        return ((u'\\.(' + s) + u')$')

    def _hy_anon_fn_19(s):
        return re.sub(u'^\\.', u'', s)

    def _hy_anon_fn_20(s):
        return (not (0L == len(s)))

    def _hy_anon_fn_21(s):
        return s.strip()

    def _hy_anon_fn_22(s):
        return s.split(u',')
    return _hy_anon_fn_17(_hy_anon_fn_18(u'|'.join(map(_hy_anon_fn_19, filter(_hy_anon_fn_20, set(map(_hy_anon_fn_21, reduce(operator.add, map(_hy_anon_fn_22, extensions)))))))))

def make_match_filter(config):

    def _hy_anon_fn_26():

        def _hy_anon_fn_24(v):
            return v.get(u'match', u'')
        matcher = make_match_filter_matcher(map(_hy_anon_fn_24, config.itervalues()))

        def _hy_anon_fn_25(path):
            return matcher.search(path)
        return _hy_anon_fn_25
    return _hy_anon_fn_26()

def executable_exists(script, label):
    if (not len(script)):
        _hy_anon_var_4 = sys.exit(_(u'Syntax error in command configuration for {} ').format(label))
    else:

        def _hy_anon_fn_31():
            scriptname = script.split(u' ')[0L]
            paths = os.environ.get(u'PATH').split(u':')

            def isexecutable(p):
                return (os.path.exists(p) and os.access(p, os.X_OK))
            if (not len(scriptname)):
                _hy_anon_var_3 = sys.exit(_(u'Syntax error in command configuration for {} ').format(label))
            else:
                if (scriptname[0L] == u'/'):
                    _hy_anon_var_2 = (scriptname if isexecutable(scriptname) else None)
                else:

                    def _hy_anon_fn_30():

                        def _hy_anon_fn_29(path):
                            return isexecutable(os.path.join(path, scriptname))
                        possibles = list(filter(_hy_anon_fn_29, paths))
                        return (possibles[0L] if len(possibles) else None)
                    _hy_anon_var_2 = _hy_anon_fn_30()
                _hy_anon_var_3 = _hy_anon_var_2
            return _hy_anon_var_3
        _hy_anon_var_4 = _hy_anon_fn_31()
    return _hy_anon_var_4

def get_working_linters(config):

    def _hy_anon_fn_34():

        def found(key):
            return executable_exists(config.get(key).get(u'command'), key)
        return set(filter(found, config.keys()))
    return _hy_anon_fn_34()

def print_linters(config):
    print(_(u'Currently supported linters:'))

    def _hy_anon_fn_36():
        working = get_working_linters(config)
        broken = (set(config.keys()) - working)
        for key in sorted(working):
            print(u'{:<14} {}'.format(key, config.get(key).get(u'comment', u'')))
        for key in sorted(broken):
            print(u'{:<14} {}'.format(key, _(u'(WARNING: executable not found)')))
    return _hy_anon_fn_36()

def base_file_filter(files):

    def _hy_anon_fn_38(f):
        return os.path.join(git_base, f)
    return map(_hy_anon_fn_38, files)

def cwd_file_filter(files):

    def _hy_anon_fn_41():
        gitcwd = os.path.join(os.path.relpath(os.getcwd(), git_base), u'')

        def _hy_anon_fn_40(f):
            return f.startswith(gitcwd)
        return base_file_filter(filter(_hy_anon_fn_40, files))
    return _hy_anon_fn_41()

def base_file_cleaner(files):

    def _hy_anon_fn_43(f):
        return f.replace(git_base, 1L)
    return map(_hy_anon_fn_43, files)
MERGE_CONFLICT_PAIRS = set([u'DD', u'DU', u'AU', u'AA', u'UD', u'UA', u'UU'])

def check_for_conflicts(files):

    def _hy_anon_fn_46():

        def _hy_anon_fn_45(_hy_anon_var_5):
            (index, workspace, filename) = _hy_anon_var_5
            (index, workspace, filename)
            return ((u'' + index) + workspace)
        status_pairs = map(_hy_anon_fn_45, files)
        conflicts = (set(MERGE_CONFLICT_PAIRS) & set(status_pairs))
        return (sys.exit(_(u'Current repository contains merge conflicts. Linters will not be run.')) if len(conflicts) else files)
    return _hy_anon_fn_46()

def remove_submodules(files):

    def _hy_anon_fn_52():

        def split_out_paths(s):
            return s.split(u' ')[2L]
        fixer_re = re.compile(u'^(\\.\\.\\/)+')

        def fixer_to_base(s):
            return fixer_re.sub(u'', s)
        submodule_entries = split_git_response([u'submodule', u'status'])

        def _hy_anon_fn_50(s):
            return fixer_to_base(split_out_paths(s))
        submodule_names = map(_hy_anon_fn_50, submodule_entries)

        def _hy_anon_fn_51(s):
            return (not (s in submodule_names))
        return filter(_hy_anon_fn_51, files)
    return _hy_anon_fn_52()

def get_porcelain_status():

    def _hy_anon_fn_57():
        cmd = [u'status', u'-z', u'--porcelain', u'--untracked-files=all', u'--ignore-submodules=all']

        def nonnull(s):
            return (len(s) > 0L)
        stream = list(filter(nonnull, get_git_response(cmd).split(u'\x00')))

        def parse_stream(acc, stream):
            if (0L == len(stream)):
                _hy_anon_var_6 = acc
            else:

                def _hy_anon_fn_55():
                    temp = stream.pop(0L)
                    index = temp[0L]
                    workspace = temp[1L]
                    filename = temp[3L:]
                    (stream.pop(0L) if (index == u'R') else None)
                    return parse_stream((acc + [(index, workspace, filename)]), stream)
                _hy_anon_var_6 = _hy_anon_fn_55()
            return _hy_anon_var_6
        return check_for_conflicts(parse_stream([], stream))
    return _hy_anon_fn_57()

def staging_list():

    def _hy_anon_fn_59(_hy_anon_var_7):
        (index, workspace, filename) = _hy_anon_var_7
        (index, workspace, filename)
        return filename

    def _hy_anon_fn_60(_hy_anon_var_8):
        (index, workspace, filename) = _hy_anon_var_8
        (index, workspace, filename)
        return (index in [u'A', u'M'])
    return map(_hy_anon_fn_59, filter(_hy_anon_fn_60, get_porcelain_status()))

def working_list():

    def _hy_anon_fn_62(_hy_anon_var_9):
        (index, workspace, filename) = _hy_anon_var_9
        (index, workspace, filename)
        return filename

    def _hy_anon_fn_63(_hy_anon_var_10):
        (index, workspace, filename) = _hy_anon_var_10
        (index, workspace, filename)
        return (workspace in [u'A', u'M', u'?'])
    return map(_hy_anon_fn_62, filter(_hy_anon_fn_63, get_porcelain_status()))

def all_list():

    def _hy_anon_fn_66():
        cmd = [u'ls-tree', u'--name-only', u'--full-tree', u'-r', u'-z', git_head]

        def _hy_anon_fn_65(s):
            return (len(s) > 0L)
        return filter(_hy_anon_fn_65, get_git_response(cmd).split(u'\x00'))
    return _hy_anon_fn_66()

def get_filelist(options):

    def _hy_anon_fn_69():
        keys = options.keys()
        working_directory_trans = (base_file_filter if len((set(keys) & set([u'base', u'every']))) else cwd_file_filter)
        file_list_generator = (staging_list if (u'staging' in keys) else (all_list if (u'all' in keys) else (working_list if True else None)))

        def _hy_anon_fn_68():
            return working_directory_trans(remove_submodules(file_list_generator()))
        return set(_hy_anon_fn_68())
    return _hy_anon_fn_69()

def staging_wrapper(run_linters):

    def _hy_anon_fn_74():

        def time_gather(f):

            def _hy_anon_fn_71():
                stats = os.stat(f)
                return (f, (stats.atime, stats.mtime))
            return _hy_anon_fn_71()
        times = list(map(time_gather, files))
        run_git_command([u'stash', u'--keep-index'])

        def _hy_anon_fn_73():
            results = run_linters()
            run_git_command([u'reset', u'--hard'])
            run_git_command([u'stash', u'pop', u'--quiet', u'--index'])
            for (filename, timepair) in times:
                os.utime(filename, timepair)
            return results
        return _hy_anon_fn_73()
    return _hy_anon_fn_74()

def workspace_wrapper(run_linters):
    return run_linters()

def pick_runner(options):

    def _hy_anon_fn_77():
        keys = options.keys()
        return (staging_wrapper if (u'staging' in keys) else workspace_wrapper)
    return _hy_anon_fn_77()

def lmap(pred, iter):
    return list(map(pred, iter))

def encode_shell_messages(prefix, messages):

    def _hy_anon_fn_80(line):
        return u'{}{}'.format(prefix, line.decode(u'utf-8'))
    return lmap(_hy_anon_fn_80, messages.splitlines())

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

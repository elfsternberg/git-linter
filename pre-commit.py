from hy.core.language import filter, flatten, is_integer, map, reduce
VERSION = '0.0.2'
import os
import re
import subprocess
import sys
CONFIG_PATH = os.path.join(os.environ.get('GIT_DIR', './.git'), 'pccs')
MODIFIED = re.compile('^[MA]\\s+(?P<name>.*)$')
CHECKS = [{'output': 'Running Jshint...', 'command': 'jshint -c {config_path}/jshint.rc {filename}', 'match_files': ['.*\\.js$'], 'print_filename': False, 'error_condition': 'error', }, {'output': 'Running Coffeelint...', 'command': 'coffeelint {filename}', 'match_files': ['.*\\.coffee$'], 'print_filename': False, 'error_condition': 'error', }, {'output': 'Running JSCS...', 'command': 'jscs -c {config_path}/jscs.rc {filename}', 'match_files': ['.*\\.js$'], 'print_filename': False, 'error_condition': 'error', }, {'output': 'Running pep8...', 'command': 'pep8 -r --ignore=E501,W293,W391 {filename}', 'match_files': ['.*\\.py$'], 'print_filename': False, 'error_condition': 'error', }, {'output': 'Running xmllint...', 'command': 'xmllint {filename}', 'match_files': ['.*\\.xml'], 'print_filename': False, 'error_condition': 'error', }]

def get_git(cmd):

    def _hy_anon_fn_1():
        fullcmd = (['git'] + cmd)
        process = subprocess.Popen(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = process.communicate()
        (out, err)
        return (out, err, process.returncode)
    return _hy_anon_fn_1()

def call_git(cmd):

    def _hy_anon_fn_3():
        fullcmd = (['git'] + cmd)
        return subprocess.call(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return _hy_anon_fn_3()

def get_cmd(cmd):

    def _hy_anon_fn_5():
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = process.communicate()
        (out, err)
        return (out, err, process.returncode)
    return _hy_anon_fn_5()

def max_code(code_pairs):

    def _hy_anon_fn_7(m, i):
        return (i[0] if (abs(i[0]) > abs(m)) else m)
    return reduce(_hy_anon_fn_7, code_pairs, 0)

def message_bodies(code_pairs):

    def _hy_anon_fn_9(i):
        return i[1]
    return lmap(_hy_anon_fn_9, code_pairs)

def matches_file(filename, match_files):

    def _hy_anon_fn_11(match_file):
        return re.compile(match_file).match(filename)
    return any(map(_hy_anon_fn_11, match_files))

def lmap(pred, iter):
    return list(map(pred, iter))

def run_external_checker(filename, check):

    def _hy_anon_fn_16():
        cmd = check['command'].format(filename=filename, config_path=CONFIG_PATH)
        (out, err, returncode) = get_cmd(cmd)
        (out, err, returncode)
        if ((out and (check.get('error_condition', 'error') == 'output')) or err or (not (returncode == 0))):

            def _hy_anon_fn_15():
                prefix = ('\t{}:'.format(filename) if check['print_filename'] else '\t')

                def _hy_anon_fn_14(line):
                    return '{}{}'.format(prefix, line.decode('utf-8'))
                output = (lmap(_hy_anon_fn_14, out.splitlines()) + ([err] if err else []))
                return [(returncode or 1), output]
            _hy_anon_var_1 = _hy_anon_fn_15()
        else:
            _hy_anon_var_1 = [0, []]
        return _hy_anon_var_1
    return _hy_anon_fn_16()

def check_file(filename, check):
    return ([0, []] if (('match_files' in check) and (not matches_file(filename, check['match_files']))) else ([0, []] if (('ignore_files' in check) and matches_file(filename, check['ignore_files'])) else (run_external_checker(filename, check) if True else None)))

def check_files(filenames, check):

    def _hy_anon_fn_20():

        def _hy_anon_fn_19(filename):
            return check_file(filename, check)
        scan_results = lmap(_hy_anon_fn_19, filenames)
        messages = ([check['output']] + message_bodies(scan_results))
        return [max_code(scan_results), messages]
    return _hy_anon_fn_20()

def get_all_files():

    def _hy_anon_fn_24():

        def build_filenames(filenames):

            def _hy_anon_fn_22(f):
                return os.path.join(filenames[0], f)
            return map(_hy_anon_fn_22, filenames[2])
        return flatten([build_filenames(o) for o in os.walk('.')])
    return _hy_anon_fn_24()

def get_some_files(against):

    def _hy_anon_fn_28():
        (out, err, returncode) = get_git(['diff-index', '--name-status', against])
        (out, err, returncode)
        lines = out.splitlines()

        def matcher(line):
            return MODIFIED.match(line.decode('utf-8'))

        def _hy_anon_fn_27(x):
            return (not (x == ''))
        return filter(_hy_anon_fn_27, [match.group('name') for match in map(matcher, lines) if match])
    return _hy_anon_fn_28()

def scan(all_files, against):
    call_git(['stash', '--keep-index'])

    def _hy_anon_fn_31():
        toscan = list((get_all_files() if all_files else get_some_files(against)))

        def _hy_anon_fn_30(check):
            return check_files(toscan, check)
        check_results = lmap(_hy_anon_fn_30, CHECKS)
        exit_code = max_code(check_results)
        messages = flatten(message_bodies(check_results))
        for line in messages:
            print(line)
        call_git(['reset', '--hard'])
        call_git(['stash', 'pop', '--quiet', '--index'])
        return exit_code
    return _hy_anon_fn_31()

def get_head_tag():

    def _hy_anon_fn_33():
        (out, err, returncode) = get_git(['rev-parse', '--verify HEAD'])
        (out, err, returncode)
        return ('4b825dc642cb6eb9a060e54bf8d69288fbee4904' if err else 'HEAD')
    return _hy_anon_fn_33()

def main(*args):
    return sys.exit(scan(((len(args) > 1) and (args[2] == '--all-files')), get_head_tag()))
if (__name__ == '__main__'):
    import sys
    :G_1235 = main(*sys.argv)
    _hy_anon_var_2 = (sys.exit(:G_1235) if is_integer(:G_1235) else None)
else:
    _hy_anon_var_2 = None

VERSION = '0.0.2'
import os
import re
import subprocess
import sys

CONFIG_PATH = os.path.join(os.environ.get('GIT_DIR', './.git'), 'pccs')
GIT_MODIFIED_PATTERN = re.compile('^[MA]\\s+(?P<name>.*)$')
CHECKS = [
    {
        'output': 'Running Jshint...',
        'command': 'jshint -c {config_path}/jshint.rc {filename}',
        'match_files': ['.*\\.js$'],
        'print_filename': False,
        'error_condition': 'error'
    },
    {
        'output': 'Running Coffeelint...',
        'command': 'coffeelint {filename}',
        'match_files': ['.*\\.coffee$'],
        'print_filename': False,
        'error_condition': 'error'
    },
    {
        'output': 'Running JSCS...',
        'command': 'jscs -c {config_path}/jscs.rc {filename}',
        'match_files': ['.*\\.js$'],
        'print_filename': False,
        'error_condition': 'error'
    },
    {
        'output': 'Running pep8...',
        'command': 'pep8 -r --ignore=E501,W293,W391 {filename}',
        'match_files': ['.*\\.py$'],
        'print_filename': False,
        'error_condition': 'error'
    },
    {
        'output': 'Running xmllint...',
        'command': 'xmllint {filename}',
        'match_files': ['.*\\.xml'],
        'print_filename': False,
        'error_condition': 'error'
    }
]


def flatten(alist):
    if isinstance(alist, list):
        if len(alist) == 0:
            return []
        first, rest = alist[0], alist[1:]
        return flatten(first) + flatten(rest)
    return [alist]


def get_git_response(cmd):
    fullcmd = (['git'] + cmd)
    process = subprocess.Popen(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate()
    (out, err)
    return (out, err, process.returncode)


def run_git_command(cmd):
    fullcmd = (['git'] + cmd)
    return subprocess.call(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_shell_response(fullcmd):
    process = subprocess.Popen(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = process.communicate()
    (out, err)
    return (out, err, process.returncode)


def derive_max_code(code_pairs):
    def find_max_code(m, i):
        if abs(i[0]) > abs(m):
            return i[0]
        return m
    return reduce(find_max_code, code_pairs, 0)


def lmap(pred, iterable):
    return list(map(pred, iterable))


def derive_message_bodies(code_pairs):
    def get_first(i):
        return i[1]
    return lmap(get_first, code_pairs)


def encode_shell_messages(prefix, messages):
    def encode(line):
        return '{}{}'.format(prefix, line.decode('utf-8'))
    return lmap(encode, messages.splitlines())


def run_external_checker(filename, check):
    cmd = check['command'].format(filename=filename, config_path=CONFIG_PATH)
    (out, err, returncode) = get_shell_response(cmd)
    if ((out and (check.get('error_condition', 'error') == 'output')) or err or (not (returncode == 0))):
        prefix = ('\t{}:'.format(filename) if check['print_filename'] else '\t')
        output = (encode_shell_messages(prefix, out) + (encode_shell_messages(prefix, err) if err else []))
        return [(returncode or 1), output]
    return [0, []]


def matches_file(filename, match_files):
    def match_one(match_file):
        return re.compile(match_file).match(filename)
    return any(map(match_one, match_files))


def check_scan_wanted(filename, check):
    if (('match_files' in check) and (not matches_file(filename, check['match_files']))):
        return False
    if (('ignore_files' in check) and matches_file(filename, check['ignore_files'])):
        return False
    return True


def check_files(filenames, check):
    def scan_wanted(filename):
        return check_scan_wanted(filename, check)
    filenames_to_check = filter(scan_wanted, filenames)

    def external_check(filename):
        return run_external_checker(filename, check)

    results_of_checks = lmap(external_check, filenames_to_check)
    messages = ([check['output']] + derive_message_bodies(results_of_checks))
    return [derive_max_code(results_of_checks), messages]


def gather_all_filenames():
    def build_filenames(filenames):
        def make_path(f):
            return os.path.join(filenames[0], f)
        return map(make_path, filenames[2])
    return list(flatten([build_filenames(o) for o in os.walk('.')]))


def gather_staged_filenames(against):
    (out, err, returncode) = get_git_response(['diff-index', '--name-status', against])
    (out, err, returncode)
    lines = out.splitlines()

    def matcher(line):
        return GIT_MODIFIED_PATTERN.match(line.decode('utf-8'))

    return [s for s in [match.group('name')
                        for match in [matcher(l) for l in lines] if match]
            if not (s == '')]


def run_checks_for(scan_all_files, against):
    run_git_command(['stash', '--keep-index'])
    filenames_to_scan = (gather_all_filenames() if scan_all_files else gather_staged_filenames(against))

    def run_check(check):
        return check_files(filenames_to_scan, check)
    results_of_scan = lmap(run_check, CHECKS)
    exit_code = derive_max_code(results_of_scan)
    messages = flatten(derive_message_bodies(results_of_scan))
    for line in messages:
        print(line)
    run_git_command(['reset', '--hard'])
    run_git_command(['stash', 'pop', '--quiet', '--index'])
    return exit_code


def get_head_tag():
    empty_repository_hash = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
    (out, err, returncode) = get_git_response(['rev-parse', '--verify HEAD'])
    (out, err, returncode)
    return (empty_repository_hash if err else 'HEAD')


def main(*args):
    scan_all_files = ((len(args) > 1) and (args[2] == u'--all-files'))
    return int(run_checks_for(scan_all_files, get_head_tag()))

if (__name__ == u'__main__'):
    import sys
    sys.exit(main(*sys.argv))

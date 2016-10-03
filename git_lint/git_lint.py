from functools import reduce
from collections import namedtuple
import getopt
import gettext
import operator
import os
import shutil
import re
import subprocess
import sys
import pprint
try:
    import configparser
except ImportError as e:
    import ConfigParser as configparser

_ = gettext.gettext


#   ___           __ _        ___             _
#  / __|___ _ _  / _(_)__ _  | _ \___ __ _ __| |___ _ _
# | (__/ _ \ ' \|  _| / _` | |   / -_) _` / _` / -_) '_|
#  \___\___/_||_|_| |_\__, | |_|_\___\__,_\__,_\___|_|
#                     |___/


def find_config_file(options, base):
    """ Returns the configuration file from a prioritized list of locations.

    Locations are prioritized as:
        1. From the command line. Fail if specified but not found
        2. The repository's root directory, as the file .git-lint
        3. The repository's root directory, as the file .git-lint/config
        4. The user's home directory, as file .git-lint
        5. The user's home directory, as the file .git-lint/config

    If no configuration file is found, this is an error.
    """

    if 'config' in options:
        config = options['config']
        configpath = os.path.abspath(config)
        if not os.path.isfile(configpath):
            sys.exit(_('Configuration file not found: {}\n').format(config))
        return configpath

    home = os.environ.get('HOME', None)
    possibles = [os.path.join(base, '.git-lint'),
                 os.path.join(base, '.git-lint/config')] + ((home and [
                     os.path.join(home, '.git-lint'),
                     os.path.join(home, '.git-lint/config')]) or [])

    matches = [p for p in possibles if os.path.isfile(p)]
    if len(matches) == 0:
        sys.exit(_('No configuration file found, tried: {}').format(':'.join(possibles)))

    return matches[0]


# (commandLineDictionary, repositoryLocation) -> (configurationDictionary | exit)
def load_config(options, base):
    """Loads the git-lint configuration file.

    Returns the configuration file as a dictionary of dictionaries.
    Performs substitutions as specified in the SafeConfigParser
    specification; the only one performed currently is the 'repodir'
    will be replaced with the base directory of the repository.
    Combined with the option to specify the .git-lint configuration as
    a directory, this allows users to keep per-project configuration
    files for specific linters.
    """

    Linter = namedtuple('Linter', ['name', 'linter'])
    path = find_config_file(options, base)
    configloader = configparser.SafeConfigParser()
    configloader.read(path)
    configloader.set('DEFAULT', 'repodir', base)
    return [Linter(section, {k: v for (k, v) in configloader.items(section)})
            for section in configloader.sections()]


#   ___ _ _
#  / __(_) |_
# | (_ | |  _|
#  \___|_|\__|
#

def get_git_response_raw(cmd):
    fullcmd = (['git'] + cmd)
    process = subprocess.Popen(fullcmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
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
    return subprocess.call(fullcmd,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           universal_newlines=True)


def get_shell_response(fullcmd):
    process = subprocess.Popen(fullcmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True,
                               universal_newlines=True)
    (out, err) = process.communicate()
    return (out, err, process.returncode)


def get_git_base():
    (out, error, returncode) = get_git_response_raw(
        ['rev-parse', '--show-toplevel'])
    return (returncode == 0 and out.rstrip()) or None


def get_git_head():
    empty_repository_hash = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
    (out, err, returncode) = get_git_response_raw(
        ['rev-parse', '--verify HEAD'])
    return ((err and empty_repository_hash) or 'HEAD')


git_base = get_git_base()
git_head = get_git_head()


#  _   _ _   _ _ _ _   _
# | | | | |_(_) (_) |_(_)___ ___
# | |_| |  _| | | |  _| / -_|_-<
#  \___/ \__|_|_|_|\__|_\___/__/
#

class MatchFilter:

    def __init__(self, config):
        self.matcher = self.make_match_filter_matcher([v.linter.get('match', '') for v in config])

    def __call__(self, path):
        return self.matcher.search(path)

    @staticmethod
    def make_match_filter_matcher(extensions):
        trimmed = [s.strip() for s in reduce(operator.add,
                                             [ex.split(',') for ex in extensions], [])]
        cleaned = [re.sub(r'^\.', '', s) for s in trimmed]
        return re.compile(r'\.' + '|'.join(cleaned) + r'$')


#   ___ _           _     _ _     _
#  / __| |_  ___ __| |__ | (_)_ _| |_ ___ _ _ ___
# | (__| ' \/ -_) _| / / | | | ' \  _/ -_) '_(_-<
#  \___|_||_\___\__|_\_\ |_|_|_||_\__\___|_| /__/
#

def executable_exists(script, label):
    if not len(script):
        sys.exit(
            _('Syntax error in command configuration for {} ').format(label))

    scriptname = script.split(' ').pop(0)
    if not len(scriptname):
        sys.exit(
            _('Syntax error in command configuration for {} ').format(label))

    def is_executable(path):
        return os.path.exists(path) and os.access(path, os.X_OK)

    if scriptname.startswith('/'):
        return (is_executable(scriptname) and scriptname) or None

    # shutil.which() doesn't appear until Python 3, darnit.
    possibles = [path for path in
                 [os.path.join(path, scriptname)
                  for path in os.environ.get('PATH').split(':')]
                 if is_executable(path)]

    return (len(possibles) and possibles.pop(0)) or False


def get_working_linter_names(config):
    return [i.name for i in config
            if executable_exists(i.linter['command'], i.name)]


def get_linter_status(config):
    working_linter_names = get_working_linter_names(config)
    broken_linter_names = (set([i.name for i in config]) - set(working_linter_names))
    return working_linter_names, broken_linter_names


#   ___     _     _ _    _          __    __ _ _
#  / __|___| |_  | (_)__| |_   ___ / _|  / _(_) |___ ___
# | (_ / -_)  _| | | (_-<  _| / _ \  _| |  _| | / -_|_-<
#  \___\___|\__| |_|_/__/\__| \___/_|   |_| |_|_\___/__/
#

def get_filelist(options, extras):
    """ Returns the list of files against which we'll run the linters. """

    def base_file_filter(files):
        """ Return the full path for all files """
        return [os.path.join(git_base, file) for file in files]

    def cwd_file_filter(filenames):
        """ Return the full path for only those files in the cwd and down """
        if os.path.samefile(os.getcwd(), git_base):
            return base_file_filter(filenames)
        gitcwd = os.path.join(os.path.relpath(os.getcwd(), git_base), '')
        return base_file_filter([filename for filename in filenames
                                 if filename.startswith(gitcwd)])

    def check_for_conflicts(filesets):
        """ Scan list of porcelain files for merge conflic state. """
        MERGE_CONFLICT_PAIRS = set(['DD', 'DU', 'AU', 'AA', 'UD', 'UA', 'UU'])
        status_pairs = set(['' + f[0] + f[1] for f in filesets])
        if len(status_pairs & MERGE_CONFLICT_PAIRS):
            sys.exit(
                _('Current repository contains merge conflicts. Linters will not be run.'))
        return filesets

    def remove_submodules(files):
        """ Remove all submodules from the list of files git-lint cares about. """

        fixer_re = re.compile('^(\\.\\.\\/)+')
        submodules = split_git_response(['submodule', 'status'])
        submodule_names = [fixer_re.sub('', submodule.split(' ')[2])
                           for submodule in submodules]
        return [file for file in files if (file not in submodule_names)]

    def get_porcelain_status():
        """ Return the status of all files in the system. """
        cmd = ['status', '-z', '--porcelain',
               '--untracked-files=all', '--ignore-submodules=all']
        stream = [entry for entry in get_git_response(cmd).split(u'\x00')
                  if len(entry) > 0]

        # Yeah, baby, recursion, the way this is meant to be handled.
        # If you have more than 999 files that need linting, you have
        # a bigger problem...
        def parse_stream(acc, stream):
            """Parse the list of files.  T

            The list is null-terminated, but is not columnar.  If
            there's an 'R' in the index state, it means the file was
            renamed and the old name is added as a column, so it's a
            special case as we accumulate the list of files.
            """

            if len(stream) == 0:
                return acc
            entry = stream.pop(0)
            (index, workspace, filename) = (entry[0], entry[1], entry[3:])
            if index == 'R':
                stream.pop(0)
            return parse_stream(acc + [(index, workspace, filename)], stream)

        return check_for_conflicts(parse_stream([], stream))

    def staging_list():
        """ Return the list of files added or modified to the stage """

        return [filename for (index, workspace, filename) in get_porcelain_status()
                if index in ['A', 'M']]

    def working_list():
        """ Return the list of files that have been modified in the workspace.

        Includes the '?' to include files that git is not currently tracking.
        """
        return [filename for (index, workspace, filename) in get_porcelain_status()
                if workspace in ['A', 'M', '?']]

    def all_list():
        """ Return all the files git is currently tracking for this repository. """
        cmd = ['ls-tree', '--name-only', '--full-tree', '-r', '-z', git_head]
        return [file for file in get_git_response(cmd).split(u'\x00')
                if len(file) > 0]

    if len(extras):
        cwd = os.path.abspath(os.getcwd())
        extras_fullpathed = set([os.path.abspath(os.path.join(cwd, f)) for f in extras])
        not_found = set([f for f in extras_fullpathed if not os.path.isfile(f)])
        return ([os.path.relpath(f, cwd) for f in (extras_fullpathed - not_found)], not_found)

    working_directory_trans = cwd_file_filter
    if 'base' in options or 'every' in options:
        working_directory_trans = base_file_filter

    file_list_generator = working_list
    if 'all' in options:
        file_list_generator = all_list
    if 'staging' in options:
        file_list_generator = staging_list

    return (working_directory_trans(remove_submodules(file_list_generator())), [])


#  ___ _             _
# / __| |_ __ _ __ _(_)_ _  __ _  __ __ ___ _ __ _ _ __ _ __  ___ _ _
# \__ \  _/ _` / _` | | ' \/ _` | \ V  V / '_/ _` | '_ \ '_ \/ -_) '_|
# |___/\__\__,_\__, |_|_||_\__, |  \_/\_/|_| \__,_| .__/ .__/\___|_|
#              |___/       |___/                  |_|  |_|


class StagingRunner:
    def __init__(self, filenames):
        self.filenames = filenames

    def __enter__(self):
        def time_gather(f):
            stats = os.stat(f)
            return (f, (stats.st_atime, stats.st_mtime))
        self.times = [time_gather(filename) for filename in self.filenames]
        run_git_command(['stash', '--keep-index'])

    def __exit__(self, type, value, traceback):
        run_git_command(['reset', '--hard'])
        run_git_command(['stash', 'pop', '--quiet', '--index'])
        for (filename, timepair) in self.times:
            os.utime(filename, timepair)


class WorkspaceRunner(object):
    def __init__(self, filenames):
        pass

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


#  ___             _ _     _
# | _ \_  _ _ _   | (_)_ _| |_   _ __  __ _ ______
# |   / || | ' \  | | | ' \  _| | '_ \/ _` (_-<_-<
# |_|_\\_,_|_||_| |_|_|_||_\__| | .__/\__,_/__/__/
#                               |_|

class Linters:
    def __init__(self, linters, filenames):
        self.linters = linters
        self.filenames = filenames

    @staticmethod
    def encode_shell_messages(prefix, messages):
        return ['{}{}'.format(prefix, line)
                for line in messages.splitlines()]

    @staticmethod
    def run_external_linter(filename, linter, linter_name):
        """Run one linter against one file.

        If the result matches the error condition specified in the configuration file,
        return the error code and messages, otherwise return nothing.
        """

        cmd = linter['command'] + ' "' + filename + '"'
        (out, err, returncode) = get_shell_response(cmd)
        failed = ((out and (linter.get('condition', 'error') == 'output')) or err or (not (returncode == 0)))
        trimmed_filename = filename.replace(git_base + '/', '', 1)
        if not failed:
            return (trimmed_filename, linter_name, 0, [])

        prefix = (((linter.get('print', 'false').strip().lower() != 'true') and '  ') or
                  '   {}: '.format(trimmed_filename))
        output = (Linters.encode_shell_messages(prefix, out) +
                  ((err and Linters.encode_shell_messages(prefix, err)) or []))
        return (trimmed_filename, linter_name, (returncode or 1), output)

    @staticmethod
    def run_one_linter(linter, filenames):
        """ Runs one linter against a set of files

        Creates a match filter for the linter, extract the files to be
        linted, and runs the linter against each file, returning the
        result as a list of successes and failures.  Failures have a
        return code and the output of the lint process.
        """
        match_filter = MatchFilter([linter])
        files = set([filename for filename in filenames if match_filter(filename)])
        return [Linters.run_external_linter(filename, linter.linter, linter.name) for filename in files]

    def __call__(self):
        """ Returns a function to run a set of linters against a set of filenames

        This returns a function because it's going to be wrapped in a
        runner to better handle stashing and restoring a staged commit.
        """
        return reduce(operator.add,
                      [Linters.run_one_linter(linter, self.filenames) for linter in self.linters], [])

    def dryrun(self):

        def dryrunonefile(filename, linter):
            trimmed_filename = filename.replace(git_base + '/', '', 1)
            return (trimmed_filename, linter.name, 0, ['    {}'.format(trimmed_filename)])

        def dryrunonce(linter, filenames):
            match_filter = MatchFilter([linter])
            files_to_check = [filename for filename in filenames if match_filter(filename)]
            return [dryrunonefile(filename, linter) for filename in files_to_check]

        return reduce(operator.add, [dryrunonce(linter, self.filenames) for linter in self.linters], [])


def run_linters(options, config, extras=[]):

    def build_config_subset(keys):
        """ Returns a subset of the configuration, with only those linters mentioned in keys """
        return [item for item in config if item.name in keys]

    """ Runs the requested linters """
    all_filenames, unfindable_filenames = get_filelist(options, extras)

    is_lintable = MatchFilter(config)

    lintable_filenames = set([filename for filename in all_filenames
                              if is_lintable(filename)])

    unlintable_filenames = set(all_filenames) - lintable_filenames

    working_linter_names, broken_linter_names = get_linter_status(config)

    cant_lint_filter = MatchFilter(build_config_subset(
        broken_linter_names))

    cant_lint_filenames = [filename for filename in lintable_filenames
                           if cant_lint_filter(filename)]

    runner = WorkspaceRunner
    if 'staging' in options:
        runner = StagingRunner

    linters = Linters(build_config_subset(working_linter_names),
                      sorted(lintable_filenames))

    if 'dryrun' in options:
        dryrun_results = linters.dryrun()
        return (dryrun_results, unlintable_filenames, cant_lint_filenames,
                broken_linter_names, unfindable_filenames)

    with runner(lintable_filenames):
        results = linters()

    return (results, unlintable_filenames, cant_lint_filenames,
            broken_linter_names, unfindable_filenames)

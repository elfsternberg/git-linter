import sys
import os.path
import gettext
import ConfigParser

_ = gettext.gettext


# (commandLineDictionary, repositoryLocation) -> (configurationFilePath | exit)

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

    home = os.path.join(os.environ.get('HOME'))
    possibles = (os.path.join(base, '.git-lint'),
                 os.path.join(base, '.git-lint/config'),
                 os.path.join(home, '.git-lint'),
                 os.path.join(home, '.git-lint/config'))

    matches = [p for p in possibles if os.path.isfile(p)]
    if len(matches) == 0:
        sys.exit(_('No configuration file found'))

    return matches[0]


# (commandLineDictionary, repositoryLocation) -> (configurationDictionary | exit)

def get_config(options, base):
    """Loads the git-lint configuration file.

    Returns the configuration file as a dictionary of dictionaries.
    Performs substitutions as specified in the SafeConfigParser
    specification; the only one performed currently is the 'repodir'
    will be replaced with the base directory of the repository.
    Combined with the option to specify the .git-lint configuration as
    a directory, this allows users to keep per-project configuration
    files for specific linters.
    """

    path = find_config_file(options, base)
    configloader = ConfigParser.SafeConfigParser()
    configloader.read(path)
    configloader.set('DEFAULT', 'repodir', base)
    return {section: {k: v for (k, v) in configloader.items(section)}
            for section in configloader.sections()}

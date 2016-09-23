import sys
import os.path
import gettext
import ConfigParser

_ = gettext.gettext


def _find_config_file(options, base):
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


def get_config(options, base):
    path = find_config_file(options, base)
    configloader = ConfigParser.SafeConfigParser()
    configloader.read(path)
    configloader.set('DEFAULT', 'repdir', base)
    return {section: {k, v for (k, v) in configloader.items(section)}
            for section in configloader.sections()}

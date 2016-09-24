from hy.core.language import filter, map, name, reduce
import os
import sys
import inspect
import getopt
import gettext

_ = gettext.gettext


# -> scriptNameString

def get_script_name():
    """ Returns the best possible name for the script. """
    if getattr(sys, 'frozen', False):
        (path, name) = os.path.split(sys.executable)
        return name

    prefix = sys.exec_prefix.upper()
    names = [name for name in [frame[1] for frame in inspect.stack()]
             if name.startswith('<') or names.upper().startswith(prefix)]
    return names.pop()


# OptionTupleList -> (getOptOptions -> dictionaryOfOptions)

def make_options_rationalizer(optlist):
    """Takes a list of option tuples, and returns a function that takes
        the output of getopt and reduces it to the longopt key and
        associated values as a dictionary.
    """

    def make_opt_assoc(prefix, pos):
        def associater(acc, it):
            acc[(prefix + it[pos])] = it[1]
            return acc
        return associater

    short_opt_assoc = make_opt_assoc('-', 0)
    long_opt_assoc = make_opt_assoc('--', 1)

    def make_full_set(acc, i):
        return long_opt_assoc(short_opt_assoc(acc, i), i)

    fullset = reduce(make_full_set, optlist, {})

    def rationalizer(acc, it):
        acc[fullset[it[0]]] = it[1]
        return acc

    return rationalizer


# (OptionTupleList, dictionaryOfOptions) -> (dictionaryOfOptions, excludedOptions)

def remove_conflicted_options(optlist, request):
    """Takes our list of option tuples, and a cleaned copy of what was
        requested from getopt, and returns a copy of the request
        without any options that are marked as superseded, along with
        the list of superseded options
    """
    def get_excluded_keys(memo, opt):
        return memo + (len(opt) > 4 and opt[4] or [])

    keys = request.keys()
    marked = [option for option in optlist if option[1] in keys]
    exclude = reduce(get_excluded_keys, marked, [])
    excluded = [key for key in keys if key in exclude]
    cleaned = {key: request[key] for key in keys
               if key not in excluded}
    return (cleaned, excluded)


class RationalOptions:

    def __init__(self, optlist, args, name='', copyright='', version='0.0.1'):
        def shortoptstogo(i):
            return i[0] + (i[2] and ':' or '')

        def longoptstogo(i):
            return i[1] + (i[2] and '=' or '')

        optstringsshort = ''.join([shortoptstogo(opt) for opt in optlist])
        optstringslong = [longoptstogo(opt) for opt in optlist]
        (options, arg) = getopt.getopt(args[1:], optstringsshort,
                                       optstringslong)

        # Turns what getopt returns into something more human-readable
        rationalize_options = make_options_rationalizer(optlist)

        # Remove any options that
        (newoptions, excluded) = remove_conflicted_options(
            optlist, reduce(rationalize_options, options, {}))

        self.optlist = optlist
        self.options = newoptions
        self.excluded = excluded
        self.filenames = arg
        self.name = (name if name else get_script_name())
        self.version = version
        self.copyright = copyright

    def get_options(self):
        return self.options

    def get_keys(self):
        return set(self.options.keys())

    def print_help(self):
        print(_('Usage: {} [options] [filenames]').format(self.name))
        for item in self.optlist:
            print(' -{:<1}  --{:<12}  {}'.format(item[0], item[1], item[3]))
        return sys.exit()

    def print_version(self):
        print('{}'.format(self.name, self.version))
        if self.copyright:
            print(self.copyright)
        return sys.exit()

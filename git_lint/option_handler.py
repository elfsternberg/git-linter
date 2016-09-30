# Copyright (C) 2015 Elf M. Sternberg
# Author: Elf M. Sternberg

from functools import reduce
import getopt

# This was a lot shorter and smarter in Hy...

# A lot of what you see here is separated from git_lint itself, since this will not be
# relevant to the operation of pre-commit.

#   ___                              _   _    _
#  / __|___ _ __  _ __  __ _ _ _  __| | | |  (_)_ _  ___
# | (__/ _ \ '  \| '  \/ _` | ' \/ _` | | |__| | ' \/ -_)
#  \___\___/_|_|_|_|_|_\__,_|_||_\__,_| |____|_|_||_\___|
#


def cleanup_options(options, commandline):
    """Takes a table of options and the commandline, and returns a
       dictionary of those options that appear on the commandline
       along with any extra arguments.

    :param List(Tuple (string, string, boolean, string, List(string))) options,
        The table of options: One-letter option, long option, takes arguments,
        Help text, list of (long) options superseded by this one.
    : param List(strings) commandline
        The arguments as received by the start-up process
    """

    def make_option_streamliner(options):

        """Takes a list of option tuples, and returns a function that takes
            the output of getopt and reduces it to the longopt key and
            associated values as a dictionary.
        """

        fullset = {}
        for option in options:
            if option[1]:
                fullset['--' + option[1]] = option[1]
                if option[0]:
                    fullset['-' + option[0]] = option[1]

        def streamliner(acc, it):
            acc[fullset[it[0]]] = it[1]
            return acc

        return streamliner

    def remove_conflicted_options(options, request):
        """Takes our list of option tuples, and a cleaned copy of what was
            requested from getopt, and returns a copy of the request
            without any options that are marked as superseded, along with
            the list of superseded options
        """
        def get_excluded_keys(memo, opt):
            return memo + ((len(opt) > 4 and opt[4]) or [])

        keys = request.keys()
        marked = [option for option in options if option[1] in keys]
        exclude = reduce(get_excluded_keys, marked, [])
        excluded = [key for key in keys if key in exclude]
        cleaned = {key: request[key] for key in keys
                   if key not in excluded}
        return (cleaned, excluded)

    def shortoptstogo(i):
        return i[0] + ((i[2] and ':') or '')

    def longoptstogo(i):
        return i[1] + ((i[2] and '=') or '')

    optstringsshort = ''.join([shortoptstogo(opt) for opt in options])
    optstringslong = [longoptstogo(opt) for opt in options]
    (chosen_options, filenames) = getopt.getopt(commandline[1:],
                                                optstringsshort,
                                                optstringslong)

    # Turns what getopt returns into something more human-readable
    streamline_options = make_option_streamliner(options)

    # Remove any options that are superseded by others.
    (ret, excluded) = remove_conflicted_options(
        options, reduce(streamline_options, chosen_options, {}))

    return (ret, filenames, excluded)

#!/usr/bin/env python
#
# Copyright (C) 2015 Elf M. Sternberg
# Author: Elf M. Sternberg
#

# This was a lot shorter and smarter in Hy...


def make_rational_options(options, commandline):
    """Takes a table of options and the commandline, and returns a
       dictionary of those options that appear on the commandline
       along with any extra arguments.

    :param List(Tuple (string, string, boolean, string, List(string))) options,
        The table of options: One-letter option, long option, takes arguments,
        Help text, list of (long) options superseded by this one.
    : param List(strings) commandline
        The arguments as received by the start-up process
    """

    def make_options_rationalizer(options):

        """Takes a list of option tuples, and returns a function that takes
            the output of getopt and reduces it to the longopt key and
            associated values as a dictionary.
        """

        fullset = {}
        for option in options:
            if not option[1]:
                continue
            if option[0]:
                fullset['-' + option[0]] = option[1]
            fullset['--' + option[1]] = option[1]

        def rationalizer(acc, it):
            acc[fullset[it[0]]] = it[1]
            return acc

        return rationalizer

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

    def shortoptstogo(i): return i[0] + ((i[2] and ':') or '')

    def longoptstogo(i): return i[1] + ((i[2] and '=') or '')

    optstringsshort = ''.join([shortoptstogo(opt) for opt in options])
    optstringslong = [longoptstogo(opt) for opt in options]
    (options, filenames) = getopt.getopt(commandline[1:],
                                         optstringsshort,
                                         optstringslong)

    # Turns what getopt returns into something more human-readable
    rationalize_options = make_options_rationalizer(options)

    # Remove any options that are superseded by others.
    (retoptions, excluded) = remove_conflicted_options(
        optlist, reduce(rationalize_options, options, {}))

    return (retoptions, filenames, excluded)

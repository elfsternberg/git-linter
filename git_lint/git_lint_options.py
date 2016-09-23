from hy.core.language import filter, map, name, reduce
import os
import sys
import inspect
import getopt
import gettext
_ = gettext.gettext

def get_script_name():
    if getattr(sys, u'frozen', False):

        def _hy_anon_fn_1():
            (path, name) = os.path.split(sys.executable)
            (path, name)
            return name()
        _hy_anon_var_1 = _hy_anon_fn_1()
    else:

        def _hy_anon_fn_4():
            prefix = sys.exec_prefix.upper()

            def _hy_anon_fn_3(a):

                def _hy_anon_fn_2():
                    fname = a[1L]
                    return (not (fname.startswith(u'<') or fname.upper().startswith(prefx)))
                _hy_anon_fn_2()
                return inspect.stack()
            names = filter(_hy_anon_fn_3)
            name = names.pop()
            return name()
        _hy_anon_var_1 = _hy_anon_fn_4()
    return _hy_anon_var_1



def make_options_rationalizer(optlist):
    """ Takes a list of option tuples, and returns a function that takes the output of getopt
        and reduces it to the longopt key and associated values.
    """

    def make_opt_assoc(prefix, pos):
        def associater(acc, it):
            acc[(prefix + it[pos])] = it[1]
            return acc
        return associater

    short_opt_assoc = make_opt_assoc(u'-', 0)
    long_opt_assoc = make_opt_assoc(u'--', 1)
    
    def make_full_set(acc, i):
        return long_opt_assoc(short_opt_assoc(acc, i), i)
    
    fullset = reduce(make_full_set, optlist, {})
    
    def rationalizer(acc, it):
        acc[fullset[it[0]]] = it[1]
        return acc

    return rationalizer


def remove_conflicted_options(optlist, config):
    keys = config.keys()
    marked = filter(lambda o: o[1] in keys, optlist)
    

    exclude = reduce
    def _hy_anon_fn_13(memo, opt):
            return (memo + (opt[4L] if (len(opt) > 4L) else []))
        exclude = reduce(_hy_anon_fn_13, marked, [])

        def _hy_anon_fn_14(key):
            return (key in exclude)
        excluded = filter(_hy_anon_fn_14, keys)

        def _hy_anon_fn_15(memo, key):
            if (not (key in excluded)):
                memo[key] = config[key]
                _hy_anon_var_2 = None
            else:
                _hy_anon_var_2 = None
            return memo
        cleaned = reduce(_hy_anon_fn_15, keys, {})
        return (cleaned, excluded)
    return _hy_anon_fn_16()


class RationalOptions:

    def __init__(self, optlist, args, name=u'', copyright=u'', version=u'0.0.1'):
        def shortoptstogo(i):
            return i[0] + (i[2] and ':' or '')

        def longoptstogo(i):
            return i[1] + (i[2] and '=' or '')
        
        optstringsshort = ''.join(map(shortoptstogo, optlist))
        optstringslong = map(longoptstogo, optlist))
        (options, arg) = getopt.getopt(args[1:], optstringsshort, optstringslong)
        rationalize_options = make_options_rationalizer(optlist)

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
            print(' -{:<1}  --{:<12}  {}'.format(item[0L], item[1L], item[3L]))
        return sys.exit()

    def print_version(self):
        print('{}'.format(self.name, self.version))
        if self.copyright:
            print(self.copyright)
        return sys.exit()

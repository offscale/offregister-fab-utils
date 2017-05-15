from itertools import imap

from fabric.api import local, sudo
from offutils import get_sorted_strnum

from offregister_fab_utils.ubuntu.version import ubuntu_version
import operator


def process_funcs(*funcs):
    def process(*args, **kwargs):
        return dict(imap(lambda g: ((g.__module__, g.__name__), g(*args, **kwargs)), funcs)) if len(funcs) else {}

    return process


def merge_funcs(*funcs):
    def outer(f):
        def inner(cache, *args, **kwargs):
            if '_merge' not in cache:
                cache['_merge'] = process_funcs(*funcs)(cache=cache, *args, **kwargs)
            else:
                cache['_merge'].update(process_funcs(*funcs)(cache=cache, *args, **kwargs))
            return f(cache=cache, *args, **kwargs)

        return inner

    return outer


def require_os_version(expected_version, op=operator.eq):
    if type(expected_version) is not float:
        expected_version = float(expected_version)

    if next((oper for oper in dir(operator) if oper in (op.__name__, '__{}__'.format(op.__name__))), None) is None:
        raise TypeError, '{op.__name__} not in operators'.format(op=op)

    def wrap(f):
        def check(cache, *args, **kwargs):
            os_version = cache['os_version'] if 'os_version' in cache else ubuntu_version()
            # TODO: check OS type                                          ^
            assert op(os_version, expected_version), '{os_version!r} not {op.__name__} {expected_version}'.format(
                os_version=os_version, op=op, expected_version=expected_version
            )
            cache['os_version'] = os_version
            return f(cache=cache, *args, **kwargs)

        return check

    return wrap


def fab_steps(module):
    """
    Extract all the fabric->offregister steps from an offregister conforming module
    Example usage:

        # in e.g.: offregister-bootstrap/offregister_bootstrap/ubuntu.py
        from offregister_inline import ubuntu as offregister_inline_ubuntu

        @merge_funcs(*fab_steps(offregister_inline_ubuntu))
        def be_awesome1(cache, *args, **kwargs):
            return 'awesome', cache['os_version']

    """
    return tuple(getattr(module, func) for func in get_sorted_strnum(dir(module)))


def timeout(duration, cmd):
    """
    :param duration: The duration of time to await the completion of the command before force exiting,
           e.g.: '120s' for 2 minutes
    :type duration: ``str``
    
    :return: string to be executed containing bash sub
    :rtype: ``str``
    """
    return '( cmdpid=$BASHPID; (sleep {duration}; kill $cmdpid) & exec {cmd} )'.format(duration=duration, cmd=cmd)

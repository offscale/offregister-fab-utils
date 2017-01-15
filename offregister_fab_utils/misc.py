from itertools import imap

from fabric.api import local, sudo

from offregister_fab_utils.fs import cmd_avail


def ubuntu_install_curl():
    command = 'curl'
    if cmd_avail(command):
        local('echo {command} is already installed'.format(command=command))
    else:
        sudo('apt-get install -y curl')


def process_funcs(*funcs):
    def process(*args, **kwargs):
        return dict(imap(lambda g: (g.__name__, g(*args, **kwargs)), funcs))

    return process


def merge_func(f):
    def inner(*args, **kwargs):
        return {'_merge': process_funcs(f)(*args, **kwargs)}

    return inner


def merge_funcs(*funcs):
    def outer(f):
        def inner(*args, **kwargs):
            return {'_merge': process_funcs(f, *funcs)(*args, **kwargs)}

        return inner

    return outer

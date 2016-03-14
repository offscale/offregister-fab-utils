from itertools import imap, ifilterfalse
from functools import partial
from operator import is_
from collections import namedtuple

from fabric.api import run, sudo, cd

from offregister_fab_utils import skip_apt_update
from offregister_fab_utils.fs import get_tempdir_fab

Package = namedtuple('Package', ('name', 'version'))


def is_installed(*packages):
    """
    :param package-name strings or Package :type splat
    :return: packages which need installed :type tuple
    """""
    return tuple(ifilterfalse(partial(is_, True), imap(
        lambda package: (run("dpkg-query --showformat='${Version}' " + '--show {}'.format(package.name),
                             warn_only=True).startswith(package.version)
                         if isinstance(package, Package)
                         else run('dpkg -s {package}'.format(package=package),
                                  quiet=True, warn_only=True).succeeded) or package,
        packages)))

def apt_depend_factory(skip_update=False):
    global skip_apt_update
    skip_apt_update = skip_update
    return apt_depends


def apt_depends(*packages):
    global skip_apt_update
    more_to_install = is_installed(*packages)
    if not more_to_install:
        return None
    elif not skip_apt_update:
        sudo('apt-get update -qq')
    return sudo('apt-get install -y {packages}'.format(
        packages=' '.join(pkg.name if isinstance(pkg, Package) else pkg for pkg in more_to_install)))


def download_and_install(url_prefix, packages):
    def one(package):
        run('curl -OL {url_prefix}{package}'.format(url_prefix=url_prefix, package=package))
        sudo('dpkg -i {package}'.format(package=package))

    with cd(get_tempdir_fab()):
        return tuple(imap(one, packages))

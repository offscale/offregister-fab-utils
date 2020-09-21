from functools import partial
from operator import is_
from collections import namedtuple
from sys import version

if version[0] == "2":
    from itertools import imap as map, ifilterfalse as filterfalse
else:
    from itertools import filterfalse

from fabric.api import run, sudo, cd

from offregister_fab_utils import skip_yum_update
from offregister_fab_utils.fs import get_tempdir_fab

Package = namedtuple("Package", ("name", "version"))


def is_installed(*packages):
    """
    :param package-name strings or Package :type splat
    :return: packages which need installed :type tuple
    """ ""
    return tuple(
        filterfalse(
            partial(is_, True),
            list(
                map(
                    lambda package: (
                        run(
                            "rpm -q --queryformat '%{VERSION}' "
                            + "{}".format(package.name),
                            warn_only=True,
                        ).startswith(package.version)
                        if isinstance(package, Package)
                        else run(
                            "rpm -q {package}".format(package=package),
                            quiet=True,
                            warn_only=True,
                        ).succeeded
                    )
                    or package,
                    packages,
                )
            ),
        )
    )


def yum_depend_factory(skip_update=False):
    global skip_yum_update
    skip_yum_update = skip_update
    return yum_depends


def yum_depends(*packages):
    global skip_yum_update
    more_to_install = is_installed(*packages)
    if not more_to_install:
        return None
    elif not skip_yum_update:
        sudo("yum check-update", quiet=True)
    return sudo(
        "yum install -y {packages}".format(
            packages=" ".join(
                pkg.name if isinstance(pkg, Package) else pkg for pkg in more_to_install
            )
        )
    )


def download_and_install(url_prefix, packages):
    def one(package):
        run(
            "curl -OL {url_prefix}{package}".format(
                url_prefix=url_prefix, package=package
            )
        )
        sudo("rpm -i {package}".format(package=package))

    with cd(get_tempdir_fab()):
        return tuple(map(one, packages))


def get_pretty_name():
    """ E.g.:  """
    name = run(
        "cat /etc/*elease | grep release | uniq"
    )  # `CentOS Linux release 7.4.1708 (Core)`
    return "{dist} {version}".format(
        dist=name.partition(" ")[0],
        version="".join(ch for ch in name if ch.isdigit() or ch == "."),
    )

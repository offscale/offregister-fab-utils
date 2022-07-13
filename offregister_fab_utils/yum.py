from functools import partial
from operator import is_
from sys import version

if version[0] == "2":
    from itertools import ifilterfalse as filterfalse
    from itertools import imap as map
else:
    from itertools import filterfalse

from offregister_fab_utils import Package
from offregister_fab_utils.fs import get_tempdir_fab


def is_installed(c, *packages):
    """
    Checks which of the provided `packages` are not installed

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param packages: ```Union[str, Package]```
    :type packages: ```Tuple[Union[str, Package]]```

    :returns: packages which need installed
    :rtype: ```Tuple[Union[str, Package]]```
    """
    return tuple(
        filterfalse(
            partial(is_, True),
            map(
                lambda package: (
                    c.run(
                        "rpm -q --queryformat '%{VERSION}' "
                        + "{}".format(package.name),
                        warn=True,
                    ).startswith(package.version)
                    if isinstance(package, Package)
                    else c.run(
                        "rpm -q {package}".format(package=package),
                        hide=True,
                        warn=True,
                    ).exited
                    == 0
                )
                or package,
                packages,
            ),
        )
    )


def yum_depend_factory(skip_update=False):
    global skip_yum_update
    skip_yum_update = skip_update
    return yum_depends


def yum_depends(c, *packages):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param packages: ```Union[str, Package]```
    :type packages: ```Tuple[Union[str, Package]]```
    """
    global skip_yum_update
    more_to_install = is_installed(*packages)
    if not more_to_install:
        return None
    elif not skip_yum_update:
        c.sudo("yum check-update", hide=True)
    return c.sudo(
        "yum install -y {packages}".format(
            packages=" ".join(
                pkg.name if isinstance(pkg, Package) else pkg for pkg in more_to_install
            )
        )
    )


def download_and_install(c, url_prefix, packages):
    """
    Download and install given packages

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param url_prefix: URL prefix
    :type url_prefix: ```str```

    :param packages: Packages to install
    :type packages: ```Iterable[str]```

    :return: List of installed packages
    :rtype: ```bool```
    """

    def one(package):
        """
        :param package: Package name
        :type package: ```str``
        """
        c.run(
            "curl -OL {url_prefix}{package}".format(
                url_prefix=url_prefix, package=package
            )
        )
        c.sudo("rpm -i {package}".format(package=package))

    with c.cd(get_tempdir_fab(c)):
        return tuple(map(one, packages))


def get_pretty_name(c):
    """
    E.g.: `precise`, `yakkety`

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :return: "{dist} {version}"
    :rtype: ```str```
    """
    name = c.run(
        "cat /etc/*elease | grep release | uniq"
    )  # `CentOS Linux release 7.4.1708 (Core)`
    return "{dist} {version}".format(
        dist=name.partition(" ")[0],
        version="".join(ch for ch in name if ch.isdigit() or ch == "."),
    )


__all__ = ["download_and_install", "get_pretty_name", "is_installed"]

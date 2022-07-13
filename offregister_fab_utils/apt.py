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
                        "dpkg-query --showformat='${Version}' "
                        + "--show {}".format(package.name),
                        warn_only=True,
                    ).startswith(package.version)
                    if isinstance(package, Package)
                    else c.run(
                        "dpkg -s {package}".format(package=package),
                        quiet=True,
                        warn_only=True,
                    ).succeeded
                )
                or package,
                packages,
            ),
        )
    )


def apt_depend_factory(skip_update=False):
    global skip_apt_update
    skip_apt_update = skip_update
    return apt_depends


def apt_depends(c, *packages):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param packages: ```Union[str, Package]```
    :type packages: ```Tuple[Union[str, Package]]```

    :return: ResultSet
    """
    global skip_apt_update
    more_to_install = is_installed(*packages)
    if not more_to_install:
        return None
    elif not skip_apt_update:
        c.sudo("apt-get update -qq")
    return c.sudo(
        "apt-get install -y {packages}".format(
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
        c.run(
            "curl -OL {url_prefix}{package}".format(
                url_prefix=url_prefix, package=package
            )
        )
        c.sudo("dpkg -i {package}".format(package=package))

    with cd(get_tempdir_fab()):
        return tuple(map(one, packages))


def get_pretty_name(c):
    """
    E.g.: `precise`, `yakkety`

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :return: $UBUNTU_CODENAME
    :rtype: ```str```
    """

    with c.prefix("source /etc/os-release"):
        name = c.run('echo ${VERSION/*, /} | { read f _ ; echo "${f,,}"; }')
        if name.stdout.startswith("1"):
            name = c.run("echo $UBUNTU_CODENAME")

    if not name:
        raise ValueError("name not set")

    return name


__all__ = ["apt_depends", "download_and_install", "get_pretty_name", "is_installed"]

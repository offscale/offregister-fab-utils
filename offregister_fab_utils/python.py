from sys import version

if version[0] == "2":
    from itertools import imap as map, ifilter as filter

from offregister_fab_utils import Package


def _cleanup_pkg_name(pkg):
    """
    :param pkg: Package
    :type pkg: ```Callable[[Union[str, Package]], str]```

    :return: Package name
    :rtype: ```str```
    """
    if isinstance(pkg, Package):
        pkg = pkg.name
    pkg = pkg.partition("[")[0]
    apache_s = "apache-"
    apache = pkg.startswith(apache_s)
    if apache:
        return pkg[len(apache_s) :]
    return pkg


def is_not_installed(c, python=None, use_sudo=False, *packages):
    """
    Check what packages are not installed

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param python:
    :type python: ```Optional[str]```

    :param use_sudo: Whether to run with `sudo`
    :type use_sudo: ```bool```

    :param packages: Packages, i.e., Tuple[Union[Package, str]]
    :type packages: ```*packages```

    :return: Packages that are not installed
    :rtype: ```Tuple[str]```
    """
    if python is None:
        python = (
            c.sudo if kwargs.get("node_sudo", kwargs.get("use_sudo", False)) else c.run
        )("which python").stdout

    packages = (package for packages_ in packages for package in packages_)

    return tuple(
        filter(
            None,
            map(
                lambda package: (c.sudo if use_sudo else c.run)(
                    "{python} -c "
                    "'import pkgutil; exit(0 if pkgutil.find_loader({package}) else 2)'".format(
                        python=python, package="'{}'".format(_cleanup_pkg_name(package))
                    ),
                    warn=True,
                    hide=True,
                ).exited
                != 0
                and package,
                packages,
            ),
        )
    )


def pip_depends(c, python=None, use_sudo=False, *packages):
    """
    Check what packages are not installed

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param python:
    :type python: ```Optional[str]```

    :param use_sudo: Whether to run with `sudo`
    :type use_sudo: ```bool```

    :param packages: Packages
    :type packages: ```*packages```
    """
    run_cmd = c.sudo if use_sudo else c.run
    if python is None:
        python = run_cmd("which python")
    more_to_install = is_not_installed(python, use_sudo, *packages)
    if not more_to_install:
        return None
    return run_cmd(
        "{python} -m pip install {packages}".format(
            python=python,
            packages=" ".join(
                "==".join((pkg.name, pkg.version)) if isinstance(pkg, Package) else pkg
                for pkg in more_to_install
            ),
        )
    )


__all__ = ["is_not_installed", "pip_depends"]

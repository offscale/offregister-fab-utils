from sys import version

if version[0] == "2":
    from itertools import imap as map, ifilter as filter

from offregister_fab_utils.apt import Package

from fabric.operations import _run_command


def _cleanup_pkg_name(pkg):  # type: (str) -> str
    pkg = pkg.partition("[")[0]
    apache_s = "apache-"
    apache = pkg.startswith(apache_s)
    if apache:
        return pkg[len(apache_s) :]
    return pkg


def is_not_installed(python=None, use_sudo=False, *packages):
    if python is None:
        python = _run_command("which python", sudo=use_sudo)

    packages = (package for packages_ in packages for package in packages_)

    return tuple(
        filter(
            None,
            map(
                lambda package: _run_command(
                    "{python} -c "
                    "'import pkgutil; exit(0 if pkgutil.find_loader({package}) else 2)'".format(
                        python=python, package="'{}'".format(_cleanup_pkg_name(package))
                    ),
                    sudo=use_sudo,
                    warn_only=True,
                    quiet=True,
                ).failed
                and package,
                packages,
            ),
        )
    )


def pip_depends(python=None, use_sudo=False, *packages):
    if python is None:
        python = _run_command("which python", sudo=use_sudo)
    more_to_install = is_not_installed(python, use_sudo, *packages)
    if not more_to_install:
        return None
    return _run_command(
        "{python} -m pip install {packages}".format(
            python=python,
            packages=" ".join(
                pkg.name if isinstance(pkg, Package) else pkg for pkg in more_to_install
            ),
        ),
        sudo=use_sudo,
    )

from invoke.exceptions import UnexpectedExit

from offregister_fab_utils import Package, skip_dnf_update
from offregister_fab_utils.misc import get_pretty_name
from offregister_fab_utils.yum import download_and_install, is_installed


def dnf_depend_factory(skip_update=False):
    global skip_dnf_update
    skip_dnf_update = skip_update
    return dnf_depends


def dnf_depends(c, *packages):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param packages: ```Union[str, Package]```
    :type packages: ```Tuple[Union[str, Package]]```
    """
    global skip_dnf_update
    more_to_install = is_installed(c, *packages)
    if not more_to_install:
        return None
    elif not skip_dnf_update:
        updated_resp = c.sudo("dnf check-update", hide=True, warn=True)
        if updated_resp == 1:
            raise UnexpectedExit(updated_resp.stderr)
    return c.sudo(
        "dnf install -y {packages}".format(
            packages=" ".join(
                pkg.name if isinstance(pkg, Package) else pkg for pkg in more_to_install
            )
        ),
        hide="stdout",
    )


_ = skip_dnf_update

__all__ = ["dnf_depends", "download_and_install", "get_pretty_name", "is_installed"]

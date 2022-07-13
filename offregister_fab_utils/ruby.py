from offregister_fab_utils import Package
from offregister_fab_utils.apt import apt_depends, is_installed


def install(c, version="2.3", *args, **kwargs):
    """
    Install Ruby

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param version: Version to install
    :type version: ```str```
    """
    if not is_installed(c, Package("ruby", version)):
        apt_depends(c, "software-properties-common")
        c.sudo("apt-add-repository -y ppa:brightbox/ruby-ng")
        apt_depends(
            c,
            "ruby{version}".format(version=version),
            "ruby{version}-dev".format(version=version),
        )


__all__ = ["install"]

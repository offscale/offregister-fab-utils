from fabric.api import sudo

from offregister_fab_utils import Package
from offregister_fab_utils.apt import apt_depends, is_installed


def install(version="2.3", *args, **kwargs):
    if not is_installed(Package("ruby", version)):
        apt_depends("software-properties-common")
        sudo("apt-add-repository -y ppa:brightbox/ruby-ng")
        apt_depends(
            "ruby{version}".format(version=version),
            "ruby{version}-dev".format(version=version),
        )

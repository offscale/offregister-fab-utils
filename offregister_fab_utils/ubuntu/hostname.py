from fabric.operations import sudo
from offregister_fab_utils.apt import apt_depends


def set_hostname(new_hostname):
    apt_depends("dbus")
    sudo("hostnamectl set-hostname {}".format(new_hostname))

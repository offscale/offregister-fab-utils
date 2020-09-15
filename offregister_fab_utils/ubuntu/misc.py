from fabric.operations import sudo, local
from offregister_fab_utils.fs import cmd_avail


def install_curl():
    command = "curl"
    if cmd_avail(command):
        local("echo {command} is already installed".format(command=command))
    else:
        sudo("apt-get install -y curl")

# -*- coding: utf-8 -*-
from offregister_fab_utils.apt import apt_depends


def install_0(c):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```
    """
    apt_depends(
        c,
        "ca-certificates" "curl" "gnupg" "lsb-release",
    )
    c.sudo("mkdir -p /etc/apt/keyrings")
    c.run("curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o docker.gpg")
    c.sudo("gpg --dearmor -o /etc/apt/keyrings/docker.gpg docker.gpg")

    c.sudo(
        'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg]'
        ' https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" |'
        " tee /etc/apt/sources.list.d/docker.list",
        quiet=True,
    )
    c.sudo("apt-get update -qq")
    apt_depends(
        c, "docker-ce", "docker-ce-cli", "containerd.io", "docker-compose-plugin"
    )
    c.sudo("systemctl enable docker")


def dockeruser_1(c, user="ubuntu"):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```
    """
    c.sudo("groupadd docker")
    c.sudo("usermod -aG docker {user}".format(user=user))


def serve_2(c):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```
    """
    c.sudo("service docker start")


__all__ = ["install_0", "dockeruser_1", "serve_2"]

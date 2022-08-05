from offregister_fab_utils.apt import apt_depends


def install_0(c, package="docker-engine"):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param package: Package name
    :type package: ```str```
    """
    uname_r = c.run("uname -r").stdout.rstrip()
    os_codename = c.run("lsb_release -cs")
    apt_depends(
        c,
        "apt-transport-https",
        "ca-certificates",
        "software-properties-common",
        "curl",
        "linux-image-extra-{}".format(uname_r),
        "linux-image-extra-virtual",
    )
    c.run("curl -fsSL https://yum.dockerproject.org/gpg | sudo apt-key add -")
    c.sudo(
        'add-apt-repository "deb https://apt.dockerproject.org/repo/ ubuntu-{} main"'.format(
            os_codename
        )
    )
    apt_depends(c, package)
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

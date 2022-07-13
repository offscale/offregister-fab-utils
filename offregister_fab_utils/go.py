from fabric.contrib.files import append

from offregister_fab_utils.fs import append_path


def install(c, version="1.5.3", arch="amd64", GOROOT="$HOME/go"):
    """
    Install Go

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param version: Version to install
    :type version: ```str```

    :param arch: Target arch
    :type arch: ```str```

    :param GOROOT: Install prefix
    :type GOROOT: ```str```
    """
    install_loc = "/usr/local"
    go_tar = "go{version}.{os}-{arch}.tar.gz".format(
        version=version, os="linux", arch=arch
    )

    c.run(
        "curl -O https://storage.googleapis.com/golang/{go_tar}".format(go_tar=go_tar)
    )
    c.sudo(
        "tar -C {install_loc} -xzf {go_tar}".format(
            install_loc=install_loc, go_tar=go_tar
        )
    )
    append_path(c, "{install_loc}/go/bin".format(install_loc=install_loc))
    c.sudo("sed -i '0,/can/{//d}' /etc/environment")
    append("/etc/environment", "GOROOT={GOROOT}".format(GOROOT=GOROOT), use_sudo=True)
    c.run("rm {go_tar}".format(go_tar=go_tar))
    # c.run('rm -rf go*')
    c.run("mkdir -p {GOROOT}".format(GOROOT=GOROOT))


__all__ = ["install"]

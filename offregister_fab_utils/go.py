from fabric.api import run, sudo
from fabric.contrib.files import append

from offregister_fab_utils.fs import append_path


def install(version='1.5.3', arch='amd64', GOROOT='$HOME/go'):
    install_loc = '/usr/local'
    go_tar = 'go{version}.{os}-{arch}.tar.gz'.format(version=version, os='linux', arch=arch)

    run('curl -O https://storage.googleapis.com/golang/{go_tar}'.format(go_tar=go_tar))
    sudo('tar -C {install_loc} -xzf {go_tar}'.format(install_loc=install_loc, go_tar=go_tar))
    append_path('{install_loc}/go/bin'.format(install_loc=install_loc))
    sudo("sed -i '0,/can/{//d}' /etc/environment")
    append('/etc/environment', 'GOROOT={GOROOT}'.format(GOROOT=GOROOT), use_sudo=True)
    run('rm {go_tar}'.format(go_tar=go_tar))
    # run('rm -rf go*')
    run('mkdir -p {GOROOT}'.format(GOROOT=GOROOT))

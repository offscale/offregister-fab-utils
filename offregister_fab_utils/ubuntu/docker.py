from fabric.operations import sudo, run

from offregister_fab_utils.apt import apt_depends


def install_0(package='docker-engine'):
    uname_r = run('uname -r')
    os_codename = run('lsb_release -cs')
    apt_depends('apt-transport-https', 'ca-certificates',
                'software-properties-common', 'curl',
                'linux-image-extra-{}'.format(uname_r),
                'linux-image-extra-virtual')
    run('curl -fsSL https://yum.dockerproject.org/gpg | sudo apt-key add -')
    sudo('add-apt-repository "deb https://apt.dockerproject.org/repo/ ubuntu-{} main"'.format(os_codename))
    apt_depends(package)
    sudo('systemctl enable docker')


def dockeruser_1(user='ubuntu'):
    sudo('groupadd docker')
    sudo('usermod -aG docker {user}'.format(user=user))


def serve_2():
    sudo('service docker start')

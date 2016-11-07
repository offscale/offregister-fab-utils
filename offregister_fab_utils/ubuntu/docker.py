from cStringIO import StringIO

from fabric.operations import sudo, put, run

from offregister_fab_utils.apt import apt_depends


def install_0():
    apt_depends('apt-transport-https ca-certificates')
    sudo('apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80'
         ' --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')
    put(StringIO('deb https://apt.dockerproject.org/repo ubuntu-trusty main'),
        '/etc/apt/sources.list.d/docker.list')
    run('apt-cache policy docker-engine')
    apt_depends('linux-image-extra-{uname}'.format(uname=run('uname -r')), 'docker-engine')

def dockeruser_1(user='ubuntu'):
    sudo('groupadd docker')
    sudo('usermod -aG docker {user}'.format(user=user))

def serve_2():
    sudo('service docker start')

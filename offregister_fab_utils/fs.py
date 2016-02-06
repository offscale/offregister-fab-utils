from fabric.api import run, settings, sudo


def get_tempdir_fab(run_command=run, **kwargs):
    return run("python -c 'from tempfile import gettempdir; print gettempdir()'", **kwargs)


def append_path(new_path):
    with settings(warn_only=True):
        installed = run('grep -q {new_path} /etc/environment'.format(new_path=new_path),
                        warn_only=True, quiet=True)

    if installed.failed:
        sudo('''sed -e '/^PATH/s/"$/:{new_path}"/g' -i /etc/environment'''.format(
            new_path=new_path.replace('/', '\/')
        ))


def cmd_avail(cmd):
    return run('command -v "{cmd}"'.format(cmd=cmd), warn_only=True, quiet=True).succeeded

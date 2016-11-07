from fabric.api import run, settings, sudo


def get_tempdir_fab(run_command=run, **kwargs):
    return (lambda r: '/tmp' if r.failed else r)(
        run_command("python -c 'from tempfile import gettempdir; print gettempdir()'",
                    quiet=True, warn_only=True, **kwargs))


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


def version_avail(cmd, version, kwarg='--version'):
    return run('{cmd} {kwarg}'.format(cmd=cmd, kwarg=kwarg), quiet=True, warn_only=True).value == version

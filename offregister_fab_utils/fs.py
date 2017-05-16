from fabric.api import run, sudo


def get_tempdir_fab(run_command=run, **kwargs):
    return (lambda r: '/tmp' if r.failed else r)(
        run_command("python -c 'from tempfile import gettempdir; print gettempdir()'",
                    quiet=True, warn_only=True, **kwargs))


def append_path(new_path, use_sudo=True):
    filename = '/etc/environment'
    installed = run('grep -q {new_path} {filename}'.format(filename=filename, new_path=new_path),
                    warn_only=True, quiet=True)

    if installed.failed:
        sudo('''sed -e '/^PATH/s/"$/:{new_path}"/g' -i {filename}'''.format(
            new_path=new_path.replace('/', '\/'), filename=filename, use_sudo=use_sudo
        ))


def cmd_avail(cmd):
    return run('command -v "{cmd}"'.format(cmd=cmd), warn_only=True, quiet=True).succeeded


def version_avail(cmd, version, kwarg='--version'):
    return run('{cmd} {kwarg}'.format(cmd=cmd, kwarg=kwarg), quiet=True, warn_only=True).value == version

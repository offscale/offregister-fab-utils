from fabric.api import run, settings, sudo


def get_tempdir_fab(run_command=run, **kwargs):
    return (lambda r: '/tmp' if r.failed else r)(
        run_command("python -c 'from tempfile import gettempdir; print gettempdir()'",
                    quiet=True, warn_only=True, **kwargs))


def append_path(new_path):
    return append_str('/etc/environment', new_path)


def append_str(filename, new_str, use_sudo=True):
    installed = run('grep -q {new_str} {filename}'.format(filename=filename, new_str=new_str),
                    warn_only=True, quiet=True, use_sudo=use_sudo)

    if installed.failed:
        sudo('''sed -e '/^PATH/s/"$/:{new_str}"/g' -i {filename}'''.format(
            new_str=new_str.replace('/', '\/'), filename=filename, use_sudo=use_sudo
        ))


def cmd_avail(cmd):
    return run('command -v "{cmd}"'.format(cmd=cmd), warn_only=True, quiet=True).succeeded


def version_avail(cmd, version, kwarg='--version'):
    return run('{cmd} {kwarg}'.format(cmd=cmd, kwarg=kwarg), quiet=True, warn_only=True).value == version

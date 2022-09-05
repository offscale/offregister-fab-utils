from os import path, remove
from tempfile import gettempdir


def get_tempdir_fab(c, run_command=None, **kwargs):
    """
    Get the tempdir using the `run_command` context

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param run_command: Run command
    :type run_command: ```Optional[Callable[[str, ...Any], Any]]```

    :return: Remote tempdir
    :rtype: ```str```
    """
    return (lambda r: "/tmp" if r.exited != 0 else r.stdout)(
        (run_command or c.run)(
            "python -c 'from tempfile import gettempdir; print gettempdir()'",
            hide=True,
            warn=True,
            **kwargs
        )
    )


def append_path(c, new_path, use_sudo=True):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param new_path: New path
    :type new_path: ```str```

    :param use_sudo: Whether to enable `sudo`
    :type use_sudo: ```bool```
    """
    filename = "/etc/environment"
    installed = c.run(
        "grep -q {new_path} {filename}".format(filename=filename, new_path=new_path),
        warn=True,
        hide=True,
    )

    if installed.exited != 0:
        c.sudo(
            """sed -e '/^PATH/s/"$/:{new_path}"/g' -i {filename}""".format(
                new_path=new_path.replace("/", "\/"),
                filename=filename,
            )
        )


def cmd_avail(c, cmd):
    """
    Check if command is available

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param cmd: Command to run
    :type cmd: ```str```
    """
    return c.run('command -v "{cmd}"'.format(cmd=cmd), warn=True, hide=True).exited == 0


def version_avail(c, cmd, version, kwarg="--version"):
    """
    Check whether required version is installed

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param cmd: Command to run
    :type cmd: ```str```

    :param version: Version required
    :type version: ```str```

    :param kwarg: CLI command to get the version
    :type kwarg: ```str```

    :return: Whether required version is installed
    :rtype: ```bool```
    """
    return (
        c.run("{cmd} {kwarg}".format(cmd=cmd, kwarg=kwarg), hide=True, warn=True).value
        == version
    )


def put_sudo(
    c, local, remote, preserve_mode=True, remote_temp_dir="/tmp", local_is_bytes=False
):
    """
    `c.put` with `use_sudo=True`

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param local: Local path of file to upload, or a file-like object, or a str/bytes if `local_is_bytes`.
    :type local: ```IO```

    :param remote: Remote path to which the local file will be written.
    :type remote: ```str```

    :param preserve_mode:
    :type preserve_mode: ```bool```

    :param remote_temp_dir:
    :type remote_temp_dir: ```str```

    :param local_is_bytes: Whether the `local` param is bytes/str
    :type local_is_bytes: ```bool```
    """
    last_slash = remote.rfind("/")
    remote_name = remote[last_slash+1:]
    temp_remote_path = "{}/{}".format(remote_temp_dir, remote_name)

    if local_is_bytes is True:
        tmp_local = path.join(gettempdir(), remote_name)
        with open(tmp_local, "w") as f:
            f.write(local)
        c.put(local=tmp_local, remote=temp_remote_path, preserve_mode=preserve_mode)
        remove(tmp_local)
    else:
        c.put(local=local, remote=temp_remote_path, preserve_mode=preserve_mode)
    c.sudo(
        "[ -d {parent_dir} ] || mkdir -p {parent_dir} ; mv '{temp_remote_path}' '{remote}'".format(
            parent_dir=remote[:last_slash],
            temp_remote_path=temp_remote_path,
            remote=remote,
        )
    )


__all__ = ["append_path", "cmd_avail", "get_tempdir_fab", "put_sudo", "version_avail"]

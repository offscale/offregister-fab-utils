def get_tempdir_fab(c, run_command, **kwargs):
    """
    Get the tempdir using the `run_command` context

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param run_command: Run command
    :type run_command: Callable[[str, ...Any], Any]
    """
    return (lambda r: "/tmp" if r.failed else r)(
        (run_command or c.run)(
            "python -c 'from tempfile import gettempdir; print gettempdir()'",
            quiet=True,
            warn_only=True,
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
        warn_only=True,
        quiet=True,
    )

    if installed.failed:
        c.sudo(
            """sed -e '/^PATH/s/"$/:{new_path}"/g' -i {filename}""".format(
                new_path=new_path.replace("/", "\/"),
                filename=filename,
                use_sudo=use_sudo,
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
    return c.run(
        'command -v "{cmd}"'.format(cmd=cmd), warn_only=True, quiet=True
    ).succeeded


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
        c.run(
            "{cmd} {kwarg}".format(cmd=cmd, kwarg=kwarg), quiet=True, warn_only=True
        ).value
        == version
    )


__all__ = ["append_path", "cmd_avail", "get_tempdir_fab", "version_avail"]

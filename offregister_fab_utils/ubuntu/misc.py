from offregister_fab_utils.fs import cmd_avail


def install_curl(c):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```
    """
    command = "curl"
    if cmd_avail(c, command):
        c.local("echo {command} is already installed".format(command=command))
    else:
        c.sudo("apt-get install -y curl")


def user_group_tuple(c, use_sudo=False):
    """
    Provide the user/group tuple (from $GROUP and $USER environment variables)

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param use_sudo: Whether to run with `sudo`
    :type use_sudo: ```bool```

    :return: User/group tuple, with group set to user if "$GROUP" is empty
    :rtype: ```Tuple[str, str]```
    """

    # One alternative: `printf '%s\t%s' "$(id -un)" "$(id -gn)"`

    return (lambda ug: (ug[0], ug[1]) if len(ug) > 1 else (ug[0], ug[0]))(
        (c.sudo if use_sudo else c.run)(
            '''printf '%s\t%s' "$USER" "$GROUP"''', hide=True, shell_escape=False
        ).split("\t")
    )


__all__ = ["install_curl", "user_group_tuple"]

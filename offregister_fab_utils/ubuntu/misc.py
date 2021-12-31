from fabric.operations import local, run, sudo

from offregister_fab_utils.fs import cmd_avail


def install_curl():
    command = "curl"
    if cmd_avail(command):
        local("echo {command} is already installed".format(command=command))
    else:
        sudo("apt-get install -y curl")


def user_group_tuple(use_sudo=False):
    """
    Provide the user/group tuple (from $GROUP and $USER environment variables)

    :param use_sudo: Whether to run with `sudo`
    :type use_sudo: ```bool```

    :returns: User/group tuple, with group set to user if "$GROUP" is empty
    :rtype: ```Tuple[str, str]```
    """

    # One alternative: `printf '%s\t%s' "$(id -un)" "$(id -gn)"`

    return (lambda ug: (ug[0], ug[1]) if len(ug) > 1 else (ug[0], ug[0]))(
        (sudo if use_sudo else run)(
            '''printf '%s\t%s' "$USER" "$GROUP"''', quiet=True, shell_escape=False
        ).split("\t")
    )

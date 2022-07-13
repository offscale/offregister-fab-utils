from offregister_fab_utils.apt import apt_depends


def set_hostname(c, new_hostname):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param new_hostname: The new hostname
    :type new_hostname: ```str```
    """
    apt_depends(c, "dbus")
    c.sudo("hostnamectl set-hostname {}".format(new_hostname))


__all__ = ["set_hostname"]

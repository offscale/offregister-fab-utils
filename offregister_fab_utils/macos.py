# -*- coding: utf-8 -*-
from os import path
from sys import modules

from pkg_resources import resource_filename


def install_upgrade_service(
    c,
    service_name,
    context,
    conf_local_filepath=None,
    root="$HOME",
    run_with_sudo=False,
):
    """
    Install|upgrade service

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param service_name: Name of service
    :type service_name: ```str```

    :param context: Dictionary with `PROGRAM` key
    :type context: ```dict```

    :param conf_local_filepath: Local filepath to config
    :type conf_local_filepath: ```Optional[str]```

    :param root: Root directory
    :type root: ```str```

    :param run_with_sudo: Whether to run parameterised with `sudo`
    :type run_with_sudo: ```bool```
    """
    conf_local_filepath = conf_local_filepath or resource_filename(
        modules[__name__].__name__, path.join("configs", "launchctl.xml")
    )
    conf_remote_filename = c.run(
        "echo {root}/Library/LaunchDaemons/{service_name}.plist".format(
            root=root, service_name=service_name
        )
    )
    upload_template_fmt(
        c,
        conf_local_filepath,
        conf_remote_filename,
        context={"LABEL": service_name, "PROGRAM": context["PROGRAM"]},
        use_sudo=True,
        backup=False,
    )
    run_cmd = c.sudo if run_with_sudo else c.run
    run_cmd(
        "launchctl load -w {conf_remote_filename}".format(
            conf_remote_filename=conf_remote_filename
        )
    )
    restart_launchctl(c, service_name, run_with_sudo=run_with_sudo)


def restart_launchctl(c, service_name, run_with_sudo):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param service_name: Name of service
    :type service_name: ```str```

    :param run_with_sudo: Whether to run parameterised with `sudo`
    :type run_with_sudo: ```bool```
    """
    run_cmd = c.sudo if run_with_sudo else c.run
    run_cmd("launchctl stop {service_name}".format(service_name=service_name))
    run_cmd("launchctl start {service_name}".format(service_name=service_name))


__all__ = ["install_upgrade_service", "restart_launchctl"]

from os import path
from sys import modules

from pkg_resources import resource_filename


def restart_systemd(c, service_name):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param service_name: Service name
    :type service_name: ```str```
    """
    c.sudo("systemctl daemon-reload")
    if (
        c.sudo(
            "systemctl status -q {service_name} --no-pager --full".format(
                service_name=service_name
            ),
            warn=True,
        ).exited
        != 0
    ):
        c.sudo(
            "systemctl start -q {service_name} --no-pager --full".format(
                service_name=service_name
            )
        )
    else:
        c.sudo(
            "systemctl stop -q {service_name} --no-pager --full".format(
                service_name=service_name
            )
        )
        c.sudo(
            "systemctl start -q {service_name} --no-pager --full".format(
                service_name=service_name
            )
        )

    return c.sudo(
        "systemctl status {service_name} --no-pager --full".format(
            service_name=service_name
        )
    )


def install_upgrade_service(c, service_name, context, conf_local_filepath=None):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param service_name: Service name
    :type service_name: ```str```

    :param context: Interpolate into context
    :type context: ```dict```

    :param conf_local_filepath: Local filepath to config
    :type conf_local_filepath: ```Optional[str]```
    """
    conf_local_filepath = conf_local_filepath or resource_filename(
        modules[__name__].__name__.rpartition(".")[0].rpartition(".")[0],
        path.join("configs", "systemd.conf"),
    )
    conf_remote_filename = "/lib/systemd/system/{service_name}.service".format(
        service_name=service_name
    )
    upload_template(
        conf_local_filepath,
        conf_remote_filename,
        context={
            "ExecStart": context["ExecStart"],
            "Environments": context["Environments"],
            "WorkingDirectory": context["WorkingDirectory"],
            "User": context["User"],
            "Group": context["Group"],
            "service_name": service_name,
        },
        use_sudo=True,
        backup=False,
    )
    return restart_systemd(c, service_name)


def disable_service(c, service):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param service: service name
    :type service: ```str```
    """
    if (
        c.sudo(
            "systemctl is-active --quiet {service}".format(service=service), warn=True
        ).exited
        == 0
    ):
        c.sudo("systemctl stop {service}".format(service=service))
        c.sudo("sudo systemctl disable {service}".format(service=service))


__all__ = ["disable_service", "install_upgrade_service", "restart_systemd"]

from os import path
from sys import modules

from fabric.api import sudo
from fabric.contrib.files import upload_template
from pkg_resources import resource_filename


def restart_systemd(service_name):
    sudo("systemctl daemon-reload")
    if sudo(
        "systemctl status -q {service_name} --no-pager --full".format(
            service_name=service_name
        ),
        warn_only=True,
    ).failed:
        sudo(
            "systemctl start -q {service_name} --no-pager --full".format(
                service_name=service_name
            )
        )
    else:
        sudo(
            "systemctl stop -q {service_name} --no-pager --full".format(
                service_name=service_name
            )
        )
        sudo(
            "systemctl start -q {service_name} --no-pager --full".format(
                service_name=service_name
            )
        )

    return sudo(
        "systemctl status {service_name} --no-pager --full".format(
            service_name=service_name
        )
    )


def install_upgrade_service(service_name, context, conf_local_filepath=None):
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
    return restart_systemd(service_name)


def disable_service(service):
    if sudo(
        "systemctl is-active --quiet {service}".format(service=service), warn_only=True
    ).succeeded:
        sudo("systemctl stop {service}".format(service=service))
        sudo("sudo systemctl disable {service}".format(service=service))

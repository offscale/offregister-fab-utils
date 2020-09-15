from sys import modules, path

from fabric.contrib.files import upload_template
from fabric.operations import run, sudo
from pkg_resources import resource_filename


def install_upgrade_service(
    service_name, context, conf_local_filepath=None, root="$HOME", run_with_sudo=False
):
    conf_local_filepath = conf_local_filepath or resource_filename(
        modules[__name__].__name__, path.join("configs", "launchctl.xml")
    )
    conf_remote_filename = run(
        "echo {root}/Library/LaunchDaemons/{service_name}.plist".format(
            root=root, service_name=service_name
        )
    )
    upload_template(
        conf_local_filepath,
        conf_remote_filename,
        context={"LABEL": service_name, "PROGRAM": context["PROGRAM"]},
        use_sudo=True,
        backup=False,
    )
    run_cmd = sudo if run_with_sudo else run
    run_cmd(
        "launchctl load -w {conf_remote_filename}".format(
            conf_remote_filename=conf_remote_filename
        )
    )
    return restart_launchctl(service_name, run_with_sudo=run_with_sudo)


def restart_launchctl(service_name, run_with_sudo):
    run_cmd = sudo if run_with_sudo else run
    run_cmd("launchctl stop {service_name}".format(service_name=service_name))
    run_cmd("launchctl stop {service_name}".format(service_name=service_name))

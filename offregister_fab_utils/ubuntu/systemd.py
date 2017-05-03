from fabric.api import sudo


def restart_systemd(service_name):
    sudo('systemctl daemon-reload')
    if sudo('systemctl status -q {service_name} --no-pager --full'.format(service_name=service_name),
            warn_only=True).failed:
        sudo('systemctl start -q {service_name} --no-pager --full'.format(service_name=service_name))
    else:
        sudo('systemctl stop -q {service_name} --no-pager --full'.format(service_name=service_name))
        sudo('systemctl start -q {service_name} --no-pager --full'.format(service_name=service_name))

    return sudo('systemctl status {service_name} --no-pager --full'.format(service_name=service_name))

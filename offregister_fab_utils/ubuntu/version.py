from fabric.operations import run


def ubuntu_version():
    """

    :return: 14.04 or 16.04 (&etc.)
    """
    return float(run('''
        while read -r l; do
            if [ "${l%"${l#????????????????}"}" = 'DISTRIB_RELEASE=' ]; then
                echo `expr substr "$l" 17 5`
                break;
            fi
        done<"/etc/lsb-release"
        ''', quiet=True, warn_only=True))

    # `lsb_release -rs` equivalent^

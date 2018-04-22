from types import DictType

from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.operations import run, sudo


def clone_or_update(repo, branch='stable', remote='origin', team='offscale',
                    skip_checkout=False, skip_reset=False, to_dir=None, use_sudo=False,
                    cmd_runner=None):
    # TODO: Properly parse the URL
    if repo[:len('http')] in frozenset(('http', 'ssh:')):
        team, _, repo = repo.rpartition('/')
        team = team[team.rfind('/') + 1:]
        rf = repo.rfind('.git')
        if rf > -1:
            repo = repo[:rf]

    to_dir = to_dir or repo
    cmd_runner = cmd_runner if cmd_runner is not None else sudo if use_sudo else run
    if exists('{to_dir}/.git'.format(to_dir=to_dir), use_sudo=use_sudo):
        with cd(to_dir):
            cmd_runner('git fetch')
            if not skip_checkout:
                cmd_runner('git checkout -f {branch}'.format(branch=branch))
            if not skip_reset:
                cmd_runner('git reset --hard {remote}/{branch}'.format(remote=remote, branch=branch))
            cmd_runner('git merge FETCH_HEAD')
        return 'updated'
    else:
        cmd_runner('mkdir -p {to_dir}'.format(to_dir=to_dir))
        cmd_runner('git clone https://github.com/{team}/{repo}.git {to_dir}'.format(
            team=team, repo=repo, to_dir=to_dir
        ))
        with cd(to_dir):
            if not skip_checkout:
                cmd_runner('git checkout -f {branch}'.format(branch=branch))
        return 'cloned'


def url_to_git_dict(static_git_url):
    if type(static_git_url) is DictType:
        requires_set = frozenset(('repo', 'team', 'branch'))
        given_keys_set = frozenset(static_git_url.keys())
        if not len(given_keys_set.difference(requires_set)):
            raise ValueError('{given_keys_set} must contain {requires_set}'.format(
                given_keys_set=given_keys_set, requires_set=requires_set))
        return static_git_url
    elif not static_git_url.startswith('https://github.com/'):
        raise NotImplementedError('Parsing of {static_git_url}'.format(static_git_url=static_git_url))

    return {
        'repo': static_git_url[static_git_url.rfind('/') + 1:],
        'team': (lambda r: r[:r.find('/')])(static_git_url[len('https://github.com/'):]),
        'branch': static_git_url[static_git_url.rfind('#') + 1:] if '#' in static_git_url else 'master'
    }


def install_hook_listener():
    raise NotImplementedError()

from types import DictType

from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.operations import run


def clone_or_update(repo, branch='stable', remote='origin',
                    team='offscale', skip_checkout=False, skip_reset=False, to_dir=None):
    if exists(repo):
        with cd(repo):
            run('git fetch')
            if not skip_checkout:
                run('git checkout -f {branch}'.format(branch=branch))
            if not skip_reset:
                run('git reset --hard {remote}/{branch}'.format(remote=remote, branch=branch))
        return 'updated'
    else:
        to_dir = to_dir or repo
        run('git clone https://github.com/{team}/{repo}.git {to_dir}'.format(team=team, repo=repo, to_dir=to_dir))
        with cd(to_dir):
            if not skip_checkout:
                run('git checkout -f {branch}'.format(branch=branch))
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
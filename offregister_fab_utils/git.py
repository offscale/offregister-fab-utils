from offutils.util import iterkeys
from patchwork.files import exists


def clone_or_update(
    c,
    repo,
    branch="stable",
    remote="origin",
    team="offscale",
    tag=None,
    skip_checkout=False,
    skip_reset=False,
    skip_clean=True,
    to_dir=None,
    depth=None,
    use_sudo=False,
    cmd_runner=None,
    reset_to_first=False,
):
    """
    `clone` or update git repo

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param repo: Repository
    :type repo: ```str```

    :param branch: Branch
    :type branch: ```str```

    :param remote: Remote
    :type remote: ```str```

    :param team: Team (on GH: organisation or individual)
    :type team: ```str```

    :param tag: Tag
    :type tag: ```Optional[str]```

    :param skip_checkout: Whether to skip `git checkout`
    :type skip_checkout: ```bool```

    :param skip_reset: Whether to skip `git reset --hard`
    :type skip_reset: ```bool```

    :param skip_clean: Whether to skip `git clean -fd`
    :type skip_clean: ```bool```

    :param to_dir: Target directory
    :type to_dir: ```bool```

    :param depth: depth
    :type depth: ```Optional[int]```

    :param use_sudo: Whether to run with `sudo`
    :type use_sudo: ```bool```

    :param cmd_runner: Use this instead of `run`
    :type cmd_runner: ```Optional[Callable[[str],None]]```

    :param reset_to_first: Whether `git reset --hard` to first commit
    :type reset_to_first: ```bool```

    :return: What occurred
    :rtype: ```Literal["updated", "cloned"]```
    """
    # TODO: Properly parse the URL
    if repo[: len("http")] in frozenset(("http", "ssh:")):
        team, _, repo = repo.rpartition("/")
        team = team[team.rfind("/") + 1 :]
        rf = repo.rfind(".git")
        if rf > -1:
            repo = repo[:rf]

    to_dir = to_dir or repo
    cmd_runner = cmd_runner if cmd_runner is not None else c.sudo if use_sudo else c.run
    if exists(c, runner=c.run, path="{to_dir}/.git".format(to_dir=to_dir)):
        with c.cd(to_dir):
            if not skip_clean:
                cmd_runner("git clean -fd")

            if not skip_reset:
                cmd_runner(
                    "git reset --hard {remote}/{branch}".format(
                        remote=remote, branch=branch
                    )
                )
                if reset_to_first:
                    cmd_runner(
                        "git reset --hard $(git rev-list --max-parents=0 --abbrev-commit HEAD)"
                    )
                    cmd_runner("git pull")
                    return "updated"

            cmd_runner("true")
            if not skip_checkout and cmd_runner("git branch --show-current").stdout != branch:
                cmd_runner(
                    "git fetch {remote} {branch} && git checkout {branch}".format(
                        branch=branch, remote=remote
                    )
                )
            if tag is not None:
                cmd_runner(
                    "git fetch --all --tags --prune && git checkout tags/{tag}".format(
                        tag=tag
                    )
                )

            cmd_runner("git merge FETCH_HEAD", warn=True)
        return "updated"
    else:
        cmd_runner("mkdir -p {to_dir}".format(to_dir=to_dir))
        cmd_runner(
            "git clone https://github.com/{team}/{repo}.git {to_dir} {depth}".format(
                team=team,
                repo=repo,
                to_dir=to_dir,
                depth="" if depth is None else "--depth={depth}".format(depth=depth),
            )
        )
        with c.cd(to_dir):
            if cmd_runner("git branch --show-current").stdout != branch:
                cmd_runner("git checkout -f {branch}".format(branch=branch))
            if tag is not None:
                cmd_runner(
                    "git fetch --all --tags --prune && git checkout tags/{tag}".format(
                        tag=tag
                    )
                )

        return "cloned"


def url_to_git_dict(static_git_url):
    """
    Parse URL into `git_dict` that can be passed along to `clone_or_update`

    :param static_git_url: URL
    :type static_git_url: ```str```

    :return: Dictionary with keys: ("repo", "team", "branch")
    :rtype: ```dict```
    """
    if isinstance(type(static_git_url), dict):
        requires_set = frozenset(("repo", "team", "branch"))
        given_keys_set = frozenset(iterkeys(static_git_url))
        if not len(given_keys_set.difference(requires_set)):
            raise ValueError(
                "{given_keys_set} must contain {requires_set}".format(
                    given_keys_set=given_keys_set, requires_set=requires_set
                )
            )
        return static_git_url
    elif not static_git_url.startswith("https://github.com/"):
        raise NotImplementedError(
            "Parsing of {static_git_url}".format(static_git_url=static_git_url)
        )

    return {
        "repo": static_git_url[static_git_url.rfind("/") + 1 :],
        "team": (lambda r: r[: r.find("/")])(
            static_git_url[len("https://github.com/") :]
        ),
        "branch": static_git_url[static_git_url.rfind("#") + 1 :]
        if "#" in static_git_url
        else "master",
    }


def install_hook_listener():
    raise NotImplementedError()


__all__ = ["clone_or_update", "url_to_git_dict"]

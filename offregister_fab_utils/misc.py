import operator
import os
from collections import namedtuple
from functools import partial
from os import path
from sys import version
from tempfile import mkdtemp

import six

if version[0] == "2":
    from itertools import imap as map

from offutils import ensure_quoted, get_sorted_strnum

from offregister_fab_utils.ubuntu.version import ubuntu_version


def process_funcs(*funcs):
    def process(*args, **kwargs):
        return (
            dict(map(lambda g: ((g.__module__, g.__name__), g(*args, **kwargs)), funcs))
            if len(funcs)
            else {}
        )

    return process


def merge_funcs(*funcs):
    def outer(f):
        def inner(cache, *args, **kwargs):
            if "_merge" not in cache:
                cache["_merge"] = process_funcs(*funcs)(cache=cache, *args, **kwargs)
            else:
                cache["_merge"].update(
                    process_funcs(*funcs)(cache=cache, *args, **kwargs)
                )
            return f(cache=cache, *args, **kwargs)

        return inner

    return outer


def require_os_version(expected_version, op=operator.eq):
    if type(expected_version) is not float:
        expected_version = float(expected_version)

    if (
        next(
            (
                oper
                for oper in dir(operator)
                if oper in (op.__name__, "__{}__".format(op.__name__))
            ),
            None,
        )
        is None
    ):
        raise TypeError("{op.__name__} not in operators".format(op=op))

    def wrap(f):
        def check(cache, *args, **kwargs):
            os_version = (
                cache["os_version"] if "os_version" in cache else ubuntu_version()
            )
            # TODO: check OS type                                          ^
            assert op(
                os_version, expected_version
            ), "{os_version!r} not {op.__name__} {expected_version}".format(
                os_version=os_version, op=op, expected_version=expected_version
            )
            cache["os_version"] = os_version
            return f(cache=cache, *args, **kwargs)

        return check

    return wrap


def fab_steps(module):
    """
    Extract all the fabric->offregister steps from an offregister conforming module
    Example usage:

        # in e.g.: offregister-bootstrap/offregister_bootstrap/ubuntu.py
        from offregister_inline import ubuntu as offregister_inline_ubuntu

        @merge_funcs(*fab_steps(offregister_inline_ubuntu))
        def be_awesome1(cache, *args, **kwargs):
            return 'awesome', cache['os_version']

    """
    return tuple(getattr(module, func) for func in get_sorted_strnum(dir(module)))


def timeout(duration, cmd):
    """
    :param duration: The duration of time to await the completion of the command before force exiting,
           e.g.: '120s' for 2 minutes
    :type duration: ``str``

    :returns: string to be executed containing bash sub
    :rtype: ``str``
    """
    return "( cmdpid=$BASHPID; (sleep {duration}; kill $cmdpid) & exec {cmd} )".format(
        duration=duration, cmd=cmd
    )


def get_load_remote_file(
    c, directory, filename, use_sudo=True, load_f=lambda ident: ident, sep="/"
):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param directory: Remote directory
    :type directory: ```str```

    :param filename: Remote filename
    :type filename: ```str```

    :param use_sudo: Whether to run with `sudo`
    :type use_sudo: ```bool```

    :param load_f: Run this function against the downloaded payload
    :type load_f: ```Callable[[Any], Any]```

    :param sep: Path separator
    :type sep: ```str```

    :return: NamedTuple of: "remote_path", "content"
    :rtype: ```NamedTuple('_', [('remote_path', str), ('content', str)])```
    """
    remote_path = "{directory}{sep}{filename}".format(
        directory=directory, sep=sep, filename=filename
    )
    tmpdir = mkdtemp(prefix="offregister")
    c.get(local_path=tmpdir, remote_path=remote_path, use_sudo=use_sudo)
    with open(path.join(tmpdir, filename)) as f:
        return namedtuple("_", ("remote_path", "content"))(remote_path, load_f(f))


def upload_template_fmt(
    c,
    filename,
    destination,
    context=None,
    use_jinja=False,
    use_fmt=False,
    template_dir=None,
    use_sudo=False,
    backup=True,
    mirror_local_mode=False,
    mode=None,
    pty=None,
    keep_trailing_newline=False,
    temp_dir="",
):
    """
    Render and upload a template text file to a remote host.

    Returns the result of the inner call to `~fabric.operations.put` -- see its
    documentation for details.

    ``filename`` should be the path to a text file, which may contain `Python
    string interpolation formatting
    <http://docs.python.org/library/stdtypes.html#string-formatting>`_ and will
    be rendered with the given context dictionary ``context`` (if given.)

    Alternately, if ``use_jinja`` is set to True and you have the Jinja2
    templating library available, Jinja will be used to render the template
    instead. Templates will be loaded from the invoking user's current working
    directory by default, or from ``template_dir`` if given.

    The resulting rendered file will be uploaded to the remote file path
    ``destination``.  If the destination file already exists, it will be
    renamed with a ``.bak`` extension unless ``backup=False`` is specified.

    By default, the file will be copied to ``destination`` as the logged-in
    user; specify ``use_sudo=True`` to use `sudo` instead.

    The ``mirror_local_mode``, ``mode``, and ``temp_dir`` kwargs are passed
    directly to an internal `~fabric.operations.put` call; please see its
    documentation for details on these two options.

    The ``pty`` kwarg will be passed verbatim to any internal
    `~fabric.operations.run`/`~fabric.operations.sudo` calls, such as those
    used for testing directory-ness, making backups, etc.

    The ``keep_trailing_newline`` kwarg will be passed when creating
    Jinja2 Environment which is False by default, same as Jinja2's
    behaviour.

    .. versionchanged:: 1.1
        Added the ``backup``, ``mirror_local_mode`` and ``mode`` kwargs.
    .. versionchanged:: 1.9
        Added the ``pty`` kwarg.
    .. versionchanged:: 1.11
        Added the ``keep_trailing_newline`` kwarg.
    .. versionchanged:: 1.11
        Added the  ``temp_dir`` kwarg.

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param filename:
    :type filename: ```str```

    :param destination:
    :type destination: ```str```

    :param context: Dictionary of vars to interpolate
    :type context: ```Optional[dict]```

    :param use_jinja: Whether to use `Jinja2` for interpolation
    :type use_jinja: ```bool```

    :param use_fmt: Whether to use `str.format` for interpolation
    :type use_fmt: ```str```

    :param template_dir:
    :type template_dir: ```Optional[str]```

    :param use_sudo: Whether to enable `sudo`
    :type use_sudo: ```bool```

    :param backup: Whether to create a backup-of-original file
    :type backup: ```bool```

    :param mirror_local_mode: Whether to `chmod` the remote file so it matches the local file's mode
    :type mirror_local_mode: ```bool```

    :param mode: Whether to `chmod` the remote file to a certain mode
    :type mode: ```Optional[int]```

    :param pty:
    :type pty: ```Optional[Any]```

    :param keep_trailing_newline: Whether to keep trailing newline
    :type keep_trailing_newline: ```bool```

    :param temp_dir: Temporary directory
    :type temp_dir: ```Optional[str]```
    """
    func = c.sudo if use_sudo else c.run
    if pty is not None:
        func = partial(func, pty=pty)
    # Normalize destination to be an actual filename, due to using StringIO
    with c.settings(c.hide("everything"), warn=True):
        if func("test -d %s" % destination.replace(" ", r"\ ")).exited == 0:
            sep = "" if destination.endswith("/") else "/"
            destination += sep + os.path.basename(filename)

    # Use mode kwarg to implement mirror_local_mode, again due to using
    # StringIO
    if mirror_local_mode and mode is None:
        mode = os.stat(apply_lcwd(filename, c.env)).st_mode
        # To prevent c.put() from trying to do this
        # logic itself
        mirror_local_mode = False

    # Process template
    text = None
    if use_jinja:
        try:
            template_dir = template_dir or os.getcwd()
            template_dir = apply_lcwd(template_dir, c.env)
            from jinja2 import Environment, FileSystemLoader

            jenv = Environment(
                loader=FileSystemLoader(template_dir),
                keep_trailing_newline=keep_trailing_newline,
            )
            text = jenv.get_template(filename).render(**context or {})
            # Force to a byte representation of Unicode, or str()ification
            # within Paramiko's SFTP machinery may cause decode issues for
            # truly non-ASCII characters.
            text = text.encode("utf-8")
        except ImportError:
            import traceback

            tb = traceback.format_exc()
            c.abort(tb + "\nUnable to import Jinja2 -- see above.")
    else:
        if template_dir:
            filename = os.path.join(template_dir, filename)
        filename = apply_lcwd(filename, c.env)
        with open(os.path.expanduser(filename)) as inputfile:
            text = inputfile.read()
        if context:
            text = text.format(**context) if use_fmt else text % context

    # Back up original file
    if backup and exists(c, runner=c.run, path=destination):
        target = destination.replace(" ", r"\ ")
        func("cp %s %s.bak" % (target, target))

    if six.PY3 is True and isinstance(text, bytes):
        text = text.decode("utf-8")

    # Upload the file.
    return c.put(
        local_path=six.StringIO(text),
        remote_path=destination,
        use_sudo=use_sudo,
        mirror_local_mode=mirror_local_mode,
        mode=mode,
        temp_dir=temp_dir,
    )


def get_user_group_tuples(c, user):
    """
    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param user: user
    :type user: ```str```

    :return: unroll with `(uid, user), (gid, group) = get_user_group_tuples('myusername')`
    :rtype: ```Generator[Tuple[Tuple[str,str,str], Tuple[str,str,str]]]```
    """
    return map(
        lambda s: (lambda p: (int(p[0]), p[2][:-1]))(
            s.partition("=")[2].partition("(")
        ),
        c.run("id {user}".format(user=user)).split(" ")[:2],
    )


def remote_newer_than(c, remote_location, time_since_epoch):
    """
    Find whether the remote is newer

    :param c: Connection
    :type c: ```fabric.connection.Connection```

    :param remote_location: Location on remote host
    :type remote_location: ```str``

    :param time_since_epoch: Time since epoch #UNIX
    :type time_since_epoch: ```int```

    :returns: Whether the remote is newer than `time_since_epoch`
    :rtype: ```bool```
    """
    last_changed = int(
        c.run(
            "stat -c '%Z' {remote_location}".format(
                remote_location=ensure_quoted(remote_location)
            ),
            warn=True,
            hide=True,
        )
        or 0
    )

    return last_changed > time_since_epoch


__all__ = [
    "get_load_remote_file",
    "get_user_group_tuples",
    "merge_funcs",
    "process_funcs",
    "remote_newer_than",
    "upload_template_fmt",
]

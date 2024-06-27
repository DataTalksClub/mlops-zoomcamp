from __future__ import annotations

import inspect
import os
import re
import sys
from glob import glob as python_glob

from dynaconf.utils import deduplicate


def _walk_to_root(path, break_at=None):
    """
    Directories starting from the given directory up to the root or break_at
    """
    if not os.path.exists(path):  # pragma: no cover
        raise OSError("Starting path not found")

    if os.path.isfile(path):  # pragma: no cover
        path = os.path.dirname(path)

    last_dir = None
    current_dir = os.path.abspath(path)
    paths = []
    while last_dir != current_dir:
        paths.append(current_dir)
        paths.append(os.path.join(current_dir, "config"))
        if break_at and current_dir == os.path.abspath(break_at):  # noqa
            break
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir
    return paths


SEARCHTREE = []


def find_file(filename=".env", project_root=None, skip_files=None, **kwargs):
    """Search in increasingly higher folders for the given file
    Returns path to the file if found, or an empty string otherwise.

    This function will build a `search_tree` based on:

    - Project_root if specified
    - Invoked script location and its parents until root
    - Current working directory

    For each path in the `search_tree` it will also look for an
    additional `./config` folder.
    """
    # If filename is an absolute path and exists, just return it
    # if the absolute path does not exist, return empty string so
    # that it can be joined and avoid IoError
    if os.path.isabs(filename):
        return filename if os.path.exists(filename) else ""

    search_tree = []
    try:
        work_dir = os.getcwd()
    except FileNotFoundError:  # pragma: no cover
        return ""
    skip_files = skip_files or []

    if project_root is not None:
        search_tree.extend(_walk_to_root(project_root, break_at=work_dir))

    script_dir = os.path.dirname(os.path.abspath(inspect.stack()[-1].filename))

    # Path to invoked script and recursively to root with its ./config dirs
    search_tree.extend(_walk_to_root(script_dir))

    # Path to where Python interpreter was invoked and recursively to root
    search_tree.extend(_walk_to_root(work_dir))

    # Don't look the same place twice
    search_tree = deduplicate(search_tree)

    global SEARCHTREE
    SEARCHTREE[:] = search_tree

    for dirname in search_tree:
        check_path = os.path.join(dirname, filename)
        if check_path in skip_files:
            continue
        if os.path.exists(check_path):
            return check_path  # First found will return

    # return empty string if not found so it can still be joined in os.path
    return ""


def read_file(path, **kwargs):
    content = ""
    with open(path, **kwargs) as open_file:
        content = open_file.read().strip()
    return content


def get_local_filename(filename):
    """Takes a filename like `settings.toml` and returns `settings.local.toml`

    Arguments:
        filename {str} -- The filename or complete path

    Returns:
        [str] -- The same name or path with `.local.` added.
    """
    name, _, extension = os.path.basename(str(filename)).rpartition(
        os.path.extsep
    )

    return os.path.join(
        os.path.dirname(str(filename)), f"{name}.local.{extension}"
    )


magic_check = re.compile("([*?[])")
magic_check_bytes = re.compile(b"([*?[])")


def has_magic(s):
    """Taken from python glob module"""
    if isinstance(s, bytes):
        match = magic_check_bytes.search(s)
    else:
        match = magic_check.search(s)
    return match is not None


def glob(
    pathname,
    *,
    root_dir=None,
    dir_fd=None,
    recursive=True,
    include_hidden=True,
):
    """Redefined std glob assuming some defaults.
    and fallback for diffente python versions."""
    glob_args = {"recursive": recursive}
    if sys.version_info >= (3, 10):
        glob_args["root_dir"] = root_dir
        glob_args["dir_fd"] = dir_fd
    if sys.version_info >= (3, 11):
        glob_args["include_hidden"] = include_hidden
    return python_glob(pathname, **glob_args)

"""This module contains Git utilities."""

from __future__ import annotations

import os
import shutil
import subprocess
import warnings
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterator

from griffe.exceptions import GitError

WORKTREE_PREFIX = "griffe-worktree-"


# TODO: Remove at some point.
def __getattr__(name: str) -> Any:
    if name == "load_git":
        warnings.warn(
            f"Importing {name} from griffe.git is deprecated. Import it from griffe.loader instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        from griffe.loader import load_git

        return load_git
    raise AttributeError


def assert_git_repo(path: str | Path) -> None:
    """Assert that a directory is a Git repository.

    Parameters:
        path: Path to a directory.

    Raises:
        OSError: When the directory is not a Git repository.
    """
    if not shutil.which("git"):
        raise RuntimeError("Could not find git executable. Please install git.")

    try:
        subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as err:
        raise OSError(f"Not a git repository: {path}") from err


def get_latest_tag(repo: str | Path) -> str:
    """Get latest tag of a Git repository.

    Parameters:
        repo: The path to Git repository.

    Returns:
        The latest tag.
    """
    if isinstance(repo, str):
        repo = Path(repo)
    if not repo.is_dir():
        repo = repo.parent
    process = subprocess.run(
        ["git", "tag", "-l", "--sort=-committerdate"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = process.stdout.strip()
    if process.returncode != 0 or not output:
        raise GitError(f"Cannot list Git tags in {repo}: {output or 'no tags'}")
    return output.split("\n", 1)[0]


def get_repo_root(repo: str | Path) -> str:
    """Get the root of a Git repository.

    Parameters:
        repo: The path to a Git repository.

    Returns:
        The root of the repository.
    """
    if isinstance(repo, str):
        repo = Path(repo)
    if not repo.is_dir():
        repo = repo.parent
    output = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=repo,
    )
    return output.decode().strip()


@contextmanager
def tmp_worktree(repo: str | Path = ".", ref: str = "HEAD") -> Iterator[Path]:
    """Context manager that checks out the given reference in the given repository to a temporary worktree.

    Parameters:
        repo: Path to the repository (i.e. the directory *containing* the `.git` directory)
        ref: A Git reference such as a commit, tag or branch.

    Yields:
        The path to the temporary worktree.

    Raises:
        OSError: If `repo` is not a valid `.git` repository
        RuntimeError: If the `git` executable is unavailable, or if it cannot create a worktree
    """
    assert_git_repo(repo)
    repo_name = Path(repo).resolve().name
    with TemporaryDirectory(prefix=f"{WORKTREE_PREFIX}{repo_name}-{ref}-") as tmp_dir:
        branch = f"griffe_{ref}"
        location = os.path.join(tmp_dir, branch)
        process = subprocess.run(
            ["git", "-C", repo, "worktree", "add", "-b", branch, location, ref],
            capture_output=True,
            check=False,
        )
        if process.returncode:
            raise RuntimeError(f"Could not create git worktree: {process.stderr.decode()}")

        try:
            yield Path(location)
        finally:
            subprocess.run(["git", "-C", repo, "worktree", "remove", branch], stdout=subprocess.DEVNULL, check=False)
            subprocess.run(["git", "-C", repo, "worktree", "prune"], stdout=subprocess.DEVNULL, check=False)
            subprocess.run(["git", "-C", repo, "branch", "-D", branch], stdout=subprocess.DEVNULL, check=False)


__all__ = ["assert_git_repo", "get_latest_tag", "get_repo_root", "tmp_worktree"]

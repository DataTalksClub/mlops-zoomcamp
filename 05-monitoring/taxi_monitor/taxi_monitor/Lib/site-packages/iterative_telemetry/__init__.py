"""Iterative Telemetry."""
import contextlib
import dataclasses
import hashlib
import json
import logging
import os
import platform
import subprocess  # nosec B404
import sys
import uuid
from functools import lru_cache, wraps
from pathlib import Path
from threading import Thread
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

import distro
import requests
from appdirs import user_config_dir  # type: ignore
from filelock import FileLock, Timeout

logger = logging.getLogger(__name__)
TOKEN = "s2s.jtyjusrpsww4k9b76rrjri.bl62fbzrb7nd9n6vn5bpqt"  # nosec B105
URL = (
    "https://iterative-telemetry.herokuapp.com"
    "/api/v1/s2s/event?ip_policy=strict"
)

DO_NOT_TRACK_ENV = "ITERATIVE_DO_NOT_TRACK"
DO_NOT_TRACK_VALUE = "do-not-track"


@dataclasses.dataclass
class TelemetryEvent:
    # pylint: disable=multiple-statements
    interface: str
    action: str
    error: Optional[str] = None
    kwargs: Dict[str, Any] = dataclasses.field(default_factory=dict)


class IterativeTelemetryLogger:
    def __init__(
        self,
        tool_name,
        tool_version,
        enabled: Union[bool, Callable] = True,
        url=URL,
        token=TOKEN,
        debug: bool = False,
    ):
        self.tool_name = tool_name
        self.tool_version = tool_version
        self.enabled = enabled
        self.url = url
        self.token = token
        self.debug = debug
        if self.debug:
            logger.setLevel(logging.DEBUG)
            logger.debug("IterativeTelemetryLogger is in debug mode")
        self._current_event: Optional[TelemetryEvent] = None

    def log_param(self, key: str, value):
        if self._current_event:
            self._current_event.kwargs[key] = value

    @contextlib.contextmanager
    def event_scope(
        self, interface: str, action: str
    ) -> Iterator[TelemetryEvent]:
        event = TelemetryEvent(interface=interface, action=action)
        tmp = self._current_event
        self._current_event = event
        try:
            yield event
        finally:
            self._current_event = tmp

    def log(
        self,
        interface: str,
        action: str = None,
        skip: Union[bool, Callable[[TelemetryEvent], bool]] = None,
    ):
        def decorator(func):
            @wraps(func)
            def inner(*args, **kwargs):
                with self.event_scope(
                    interface, action or func.__name__
                ) as event:
                    try:
                        return func(*args, **kwargs)
                    except Exception as exc:
                        event.error = exc.__class__.__name__
                        raise
                    finally:
                        if (
                            skip is None
                            or (callable(skip) and not skip(event))
                            or not skip
                        ):
                            self.send_event(
                                event.interface,
                                event.action,
                                event.error,
                                **event.kwargs,
                            )

            return inner

        return decorator

    def send_cli_call(self, cmd_name: str, error: str = None, **kwargs):
        self.send_event("cli", cmd_name, error=error, **kwargs)

    def send_event(
        self,
        interface: str,
        action: str,
        error: str = None,
        use_thread: bool = False,
        use_daemon: bool = True,
        **kwargs,
    ):
        self.send(
            {
                "interface": interface,
                "action": action,
                "error": error,
                "extra": kwargs,
            },
            use_thread=use_thread,
            use_daemon=use_daemon,
        )

    def is_enabled(self):
        return (
            os.environ.get(DO_NOT_TRACK_ENV, None) is None and self.enabled()
            if callable(self.enabled)
            else self.enabled and find_or_create_user_id() is not None
        )

    def send(
        self,
        payload: Dict[str, Any],
        use_thread: bool = False,
        use_daemon: bool = True,
    ):
        if not self.is_enabled():
            return
        payload.update(self._runtime_info())
        if use_thread and use_daemon:
            raise ValueError(
                "use_thread and use_daemon cannot be true at the same time"
            )
        logger.debug("Sending payload %s", payload)
        impl = self._send
        if use_daemon:
            impl = self._send_daemon
        if use_thread:
            impl = self._send_thread
        impl(payload)

    def _send_daemon(self, payload):
        cmd = (
            f"import requests;requests.post('{self.url}',"
            f"params={{'token':'{self.token}'}},json={payload})"
        )

        if os.name == "nt":

            from subprocess import (  # nosec B404
                CREATE_NEW_PROCESS_GROUP,
                CREATE_NO_WINDOW,
                STARTF_USESHOWWINDOW,
                STARTUPINFO,
            )

            detached_flags = CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
            startupinfo = STARTUPINFO()
            startupinfo.dwFlags |= STARTF_USESHOWWINDOW
            # pylint: disable=consider-using-with
            subprocess.Popen(  # nosec B603
                [sys.executable, "-c", cmd],
                creationflags=detached_flags,
                close_fds=True,
                startupinfo=startupinfo,
            )
        elif os.name == "posix":
            # pylint: disable=consider-using-with
            subprocess.Popen(  # nosec B603
                [sys.executable, "-c", cmd],
                close_fds=True,
            )
        else:
            raise NotImplementedError

    def _send_thread(self, payload):
        Thread(target=self._send, args=[payload]).start()

    def _send(self, payload):
        try:
            requests.post(
                self.url, params={"token": self.token}, json=payload, timeout=2
            )
        except Exception:  # pylint: disable=broad-except
            logger.debug("failed to send analytics report", exc_info=True)

    def _runtime_info(self):
        """
        Gather information from the environment where DVC runs to fill a report
        """
        ci_id = _generate_ci_id()
        if ci_id:
            group_id, user_id = ci_id
        else:
            group_id, user_id = None, find_or_create_user_id()
        major, minor, patch, *_ = sys.version_info

        return {
            "python_version": {"major": major, "minor": minor, "patch": patch},
            "tool_name": self.tool_name,
            "tool_version": self.tool_version,
            "user_id": user_id,
            "group_id": group_id,
            # "scm_class": _scm_in_use(),
            **_system_info(),
        }


def _system_info():
    system = platform.system()

    if system == "Windows":
        # pylint: disable=no-member
        version = sys.getwindowsversion()
        return {
            "os_name": "windows",
            "os_version": f"{version.build}.{version.major}."
            f"{version.minor}-{version.service_pack}",
        }

    if system == "Darwin":
        return {
            "os_name": "mac",
            "os_version": platform.mac_ver()[0],
        }  # TODO do we include arch here?

    if system == "Linux":
        # TODO distro.id() and distro.like()?
        return {
            "os_name": "linux",
            "os_version": distro.version(),
        }

    # We don't collect data for any other system.
    raise NotImplementedError


def _generate_id():
    """A randomly generated ID string"""
    return str(uuid.uuid4())


_ci_id_generators: List[Callable[[], Optional[Tuple[str, str]]]] = []


def ci_id_generator(func):
    _ci_id_generators.append(func)
    return lru_cache()(func)


@ci_id_generator
def _generate_github_id():
    """group_id = "$GITHUB_SERVER_URL/$(dirname "$GITHUB_REPOSITORY")"
    user_id = "$(gh api users/$GITHUB_ACTOR --jq '.name, .login, .id' |
                 xargs echo)"""
    if not os.environ.get("GITHUB_ACTIONS"):
        return None

    server_url = os.environ.get("GITHUB_SERVER_URL")
    repository = os.environ.get("GITHUB_REPOSITORY")
    actor = os.environ.get("GITHUB_ACTOR")
    group_id = f"{server_url}/{os.path.dirname(repository)}"
    try:
        user_id = subprocess.check_output(  # nosec B603, B607
            ["gh", "api", f"users/{actor}", "--jq", ".name, .login, .id"],
            text=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return None
    return group_id, user_id


@ci_id_generator
def _generate_gitlab_id():
    """group_id = "$CI_SERVER_URL/$CI_PROJECT_ROOT_NAMESPACE"
    user_id = "$GITLAB_USER_NAME $GITLAB_USER_LOGIN $GITLAB_USER_ID"""
    user_name = os.environ.get("GITLAB_USER_NAME")
    if not user_name:
        return None
    server_url = os.environ.get("CI_SERVER_URL")
    root_namespace = os.environ.get("CI_PROJECT_ROOT_NAMESPACE")
    user_login = os.environ.get("GITLAB_USER_LOGIN")
    user_id = os.environ.get("GITLAB_USER_ID")

    group_id = f"{server_url}/{root_namespace}"
    user_id = f"{user_name} {user_login} {user_id}"
    return group_id, user_id


@ci_id_generator
def _generate_bitbucket_id():
    """group_id = "$BITBUCKET_WORKSPACE"
    user_id = "$(git log -1 --pretty=format:'%ae')"""
    group_id = os.environ.get("BITBUCKET_WORKSPACE")
    if not group_id:
        return None
    try:
        user_id = subprocess.check_output(  # nosec B603, B607
            ["git", "log", "-1", "--pretty=format:'%ae'"], text=True
        )
        return group_id, user_id
    except subprocess.SubprocessError:
        return None


@ci_id_generator
def _generate_generic_ci_id():
    return None


def _generate_ci_id():
    for generator in _ci_id_generators:
        res = generator()
        if res is not None:
            return tuple(map(deterministic, res))
    return None


def _read_user_id(config_file: Path):
    try:
        with config_file.open(encoding="utf8") as fobj:
            return json.load(fobj)["user_id"]
    except (FileNotFoundError, ValueError, KeyError):
        pass
    return None


def _read_user_id_locked(config_file: Path):
    lockfile = str(config_file.with_suffix(".lock"))
    if config_file.parent.is_dir():
        with FileLock(lockfile, timeout=5):
            return _read_user_id(config_file)
    return None


@lru_cache(None)
def find_or_create_user_id():
    """
    The user's ID is stored on a file under the global config directory.
    The file should contain a JSON with a "user_id" key:
        {"user_id": "16fd2706-8baf-433b-82eb-8c7fada847da"}
    IDs are generated randomly with UUID4.
    """
    config_file = Path(
        user_config_dir(os.path.join("iterative", "telemetry"), False)
    )
    config_file.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    lockfile = str(config_file.with_suffix(".lock"))
    # DVC backwards-compatibility
    config_file_old = Path(
        user_config_dir(os.path.join("dvc", "user_id"), "iterative")
    )

    try:
        with FileLock(  # pylint: disable=abstract-class-instantiated
            lockfile, timeout=5
        ):
            user_id = _read_user_id(config_file)
            if user_id is None:
                try:
                    user_id = _read_user_id_locked(config_file_old)
                except Timeout:
                    logger.debug(
                        "Failed to acquire %s",
                        config_file_old.with_suffix(".lock"),
                    )
                    return None
                if user_id is None:
                    user_id = _generate_id()
                with config_file.open(mode="w", encoding="utf8") as fobj:
                    json.dump({"user_id": user_id}, fobj)
    except Timeout:
        logger.debug("Failed to acquire %s", lockfile)
    return user_id if user_id.lower() != DO_NOT_TRACK_VALUE.lower() else None


def deterministic(data: str) -> uuid.UUID:
    namespace = uuid.uuid5(uuid.NAMESPACE_DNS, "iterative.ai")
    name = hashlib.scrypt(
        password=data.encode(),
        salt=namespace.bytes,
        n=1 << 16,
        r=8,
        p=1,
        maxmem=128 * 1024**2,
        dklen=8,
    )
    return uuid.uuid5(namespace, name.hex())

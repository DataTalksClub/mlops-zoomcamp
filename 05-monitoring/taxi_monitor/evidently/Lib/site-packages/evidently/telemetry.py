import json
import os
from functools import lru_cache
from pathlib import Path

import iterative_telemetry
from appdirs import user_config_dir  # type: ignore
from filelock import FileLock
from filelock import Timeout
from iterative_telemetry import DO_NOT_TRACK_VALUE
from iterative_telemetry import IterativeTelemetryLogger
from iterative_telemetry import _generate_id
from iterative_telemetry import _read_user_id
from iterative_telemetry import logger

import evidently

TOKEN = "s2s.5xmxpip2ax4ut5rrihfjhb.uqcoh71nviknmzp77ev6rd"


@lru_cache(None)
def find_or_create_user_id():
    """
    The user's ID is stored on a file under the global config directory.
    The file should contain a JSON with a "user_id" key:
        {"user_id": "16fd2706-8baf-433b-82eb-8c7fada847da"}
    IDs are generated randomly with UUID4.
    """
    config_file = Path(user_config_dir(os.path.join("evidentlyai", "telemetry"), False))
    config_file.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    lockfile = str(config_file.with_suffix(".lock"))

    try:
        with FileLock(lockfile, timeout=5):  # pylint: disable=abstract-class-instantiated
            user_id = _read_user_id(config_file)

            if user_id is None:
                user_id = _generate_id()
            with config_file.open(mode="w", encoding="utf8") as fobj:
                json.dump({"user_id": user_id}, fobj)
    except Timeout:
        logger.debug("Failed to acquire %s", lockfile)
    return user_id if user_id.lower() != DO_NOT_TRACK_VALUE.lower() else None


iterative_telemetry.find_or_create_user_id = find_or_create_user_id
DO_NOT_TRACK_ENV = "DO_NOT_TRACK"
event_logger = IterativeTelemetryLogger(
    "evidently",
    evidently.__version__,
    url="http://35.232.253.5:8000/api/v1/s2s/event?ip_policy=strict",
    token=TOKEN,
    enabled=lambda: os.environ.get(DO_NOT_TRACK_ENV, None) is None,
)


def main():
    event_logger.send_event("test", "test_action")


if __name__ == "__main__":
    main()

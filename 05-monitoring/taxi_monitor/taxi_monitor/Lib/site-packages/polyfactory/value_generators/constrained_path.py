from os.path import realpath
from pathlib import Path
from typing import Literal, cast

from faker import Faker


def handle_constrained_path(constraint: Literal["file", "dir", "new"], faker: Faker) -> Path:
    if constraint == "new":
        return cast("Path", faker.file_path(depth=1, category=None, extension=None))
    if constraint == "file":
        return Path(realpath(__file__))
    return Path(realpath(__file__)).parent

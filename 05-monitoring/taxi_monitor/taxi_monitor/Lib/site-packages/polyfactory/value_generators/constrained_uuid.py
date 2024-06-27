from typing import Literal, cast
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid5

from faker import Faker

UUID_VERSION_1 = 1
UUID_VERSION_3 = 3
UUID_VERSION_4 = 4
UUID_VERSION_5 = 5


def handle_constrained_uuid(uuid_version: Literal[1, 3, 4, 5], faker: Faker) -> UUID:
    """Generate a UUID based on the version specified.

    Args:
        uuid_version: The version of the UUID to generate.
        faker: The Faker instance to use.

    Returns:
        The generated UUID.
    """
    if uuid_version == UUID_VERSION_1:
        return uuid1()
    if uuid_version == UUID_VERSION_3:
        return uuid3(NAMESPACE_DNS, faker.pystr())
    if uuid_version == UUID_VERSION_4:
        return cast("UUID", faker.uuid4())
    if uuid_version == UUID_VERSION_5:
        return uuid5(NAMESPACE_DNS, faker.pystr())
    msg = f"Unknown UUID version: {uuid_version}"
    raise ValueError(msg)

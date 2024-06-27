from .reader import Reader
from .timezone import Timezone


def read(name, extend=True):  # type: (str, bool) -> Timezone
    """
    Read the zoneinfo structure for a given timezone name.
    """
    return Reader(extend=extend).read_for(name)


def read_file(path, extend=True):  # type: (str, bool) -> Timezone
    """
    Read the zoneinfo structure for a given path.
    """
    return Reader(extend=extend).read(path)

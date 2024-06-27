# -*- coding: utf-8 -*-

import os

from .exceptions import TimezoneNotFound
from ._timezones import timezones
from ._compat import FileNotFoundError


DEFAULT_DIRECTORY = os.path.join(
    os.path.dirname(__file__),
    'zoneinfo'
)

_DIRECTORY = os.getenv('PYTZDATA_TZDATADIR', DEFAULT_DIRECTORY)

_TIMEZONES = {}

INVALID_ZONES = ['Factory', 'leapseconds', 'localtime', 'posixrules']


def tz_file(name):
    """
    Open a timezone file from the zoneinfo subdir for reading.

    :param name: The name of the timezone.
    :type name: str

    :rtype: file
    """
    try:
        filepath = tz_path(name)

        return open(filepath, 'rb')
    except TimezoneNotFound:
        # http://bugs.launchpad.net/bugs/383171 - we avoid using this
        # unless absolutely necessary to help when a broken version of
        # pkg_resources is installed.
        try:
            from pkg_resources import resource_stream
        except ImportError:
            resource_stream = None

        if resource_stream is not None:
            try:
                return resource_stream(__name__, 'zoneinfo/' + name)
            except FileNotFoundError:
                return tz_path(name)

        raise


def tz_path(name):
    """
    Return the path to a timezone file.

    :param name: The name of the timezone.
    :type name: str

    :rtype: str
    """
    if not name:
        raise ValueError('Invalid timezone')

    name_parts = name.lstrip('/').split('/')

    for part in name_parts:
        if part == os.path.pardir or os.path.sep in part:
            raise ValueError('Bad path segment: %r' % part)

    filepath = os.path.join(_DIRECTORY, *name_parts)

    if not os.path.exists(filepath):
        raise TimezoneNotFound('Timezone {} not found at {}'.format(name, filepath))

    return filepath


def set_directory(directory=None):
    global _DIRECTORY

    if directory is None:
        directory = os.getenv('PYTZDATA_TZDATADIR', DEFAULT_DIRECTORY)

    _DIRECTORY = directory


def get_timezones():
    """
    Get the supported timezones.

    The list will be cached unless you set the "fresh" attribute to True.

    :param fresh: Whether to get a fresh list or not
    :type fresh: bool

    :rtype: tuple
    """
    base_dir = _DIRECTORY
    zones = ()

    for root, dirs, files in os.walk(base_dir):
        for basename in files:
            zone = os.path.join(root, basename)
            if os.path.isdir(zone):
                continue

            zone = os.path.relpath(zone, base_dir)

            with open(os.path.join(root, basename), 'rb') as fd:
                if fd.read(4) == b'TZif' and zone not in INVALID_ZONES:
                    zones = zones + (zone,)

    return tuple(sorted(zones))


def _get_suffix(name):
    i = name.rfind('.')
    if 0 < i < len(name) - 1:
        return name[i:]
    else:
        return ''

class ZoneinfoError(Exception):

    pass


class InvalidZoneinfoFile(ZoneinfoError):

    pass


class InvalidTimezone(ZoneinfoError):
    def __init__(self, name):
        super(InvalidTimezone, self).__init__('Invalid timezone "{}"'.format(name))


class InvalidPosixSpec(ZoneinfoError):
    def __init__(self, spec):
        super(InvalidPosixSpec, self).__init__("Invalid POSIX spec: {}".format(spec))

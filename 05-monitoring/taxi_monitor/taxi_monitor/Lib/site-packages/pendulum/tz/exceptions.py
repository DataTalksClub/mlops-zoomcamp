class TimezoneError(ValueError):

    pass


class NonExistingTime(TimezoneError):

    message = "The datetime {} does not exist."

    def __init__(self, dt):
        message = self.message.format(dt)

        super(NonExistingTime, self).__init__(message)


class AmbiguousTime(TimezoneError):

    message = "The datetime {} is ambiguous."

    def __init__(self, dt):
        message = self.message.format(dt)

        super(AmbiguousTime, self).__init__(message)

import functools
import inspect
import warnings

string_types = (type(b""), type(""))


def warn_deprecation(text):
    warnings.warn(text, category=DeprecationWarning, stacklevel=2)


def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    if isinstance(reason, string_types):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = f"Call to deprecated class {func1.__name__} ({reason})."
            else:
                fmt1 = f"Call to deprecated function {func1.__name__} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warn_deprecation(fmt1)
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = f"Call to deprecated class {func2.__name__}."
        else:
            fmt2 = f"Call to deprecated function {func2.__name__}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warn_deprecation(fmt2)
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))

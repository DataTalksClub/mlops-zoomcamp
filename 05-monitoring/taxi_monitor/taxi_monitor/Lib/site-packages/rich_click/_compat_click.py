import click


try:
    click_version = click.__version__
except Exception:
    # Click 9+ deprecated __version__, so all these checks must necessarily be False if __version__ doesn't exist.
    CLICK_IS_BEFORE_VERSION_8X = False
    CLICK_IS_BEFORE_VERSION_9X = False
    CLICK_IS_VERSION_80 = False
else:
    _major = int(click_version.split(".")[0])
    _minor = int(click_version.split(".")[1])

    CLICK_IS_BEFORE_VERSION_8X = _major < 8
    CLICK_IS_BEFORE_VERSION_9X = _major < 9
    CLICK_IS_VERSION_80 = _major == 8 and _minor == 0


if CLICK_IS_BEFORE_VERSION_8X:
    import warnings

    warnings.warn(
        "rich-click support for click 7.x is deprecated and will be removed soon."
        " Please upgrade click to a newer version.",
        DeprecationWarning,
        stacklevel=2,
    )

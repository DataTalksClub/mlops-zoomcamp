# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""QString compatibility."""


def qstring_length(text):
    """
    Tries to compute what the length of an utf16-encoded QString would be.
    """
    utf16_text = text.encode('utf16')
    length = len(utf16_text) // 2
    # Remove Byte order mark.
    # TODO: All unicode Non-characters should be removed
    if utf16_text[:2] in [b'\xff\xfe', b'\xff\xff', b'\xfe\xff']:
        length -= 1
    return length

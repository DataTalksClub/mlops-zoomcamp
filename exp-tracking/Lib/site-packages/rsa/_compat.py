#  Copyright 2011 Sybren A. Stüvel <sybren@stuvel.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Python compatibility wrappers."""

from struct import pack


def byte(num: int) -> bytes:
    """
    Converts a number between 0 and 255 (both inclusive) to a base-256 (byte)
    representation.

    :param num:
        An unsigned integer between 0 and 255 (both inclusive).
    :returns:
        A single byte.
    """
    return pack("B", num)


def xor_bytes(b1: bytes, b2: bytes) -> bytes:
    """
    Returns the bitwise XOR result between two bytes objects, b1 ^ b2.

    Bitwise XOR operation is commutative, so order of parameters doesn't
    generate different results. If parameters have different length, extra
    length of the largest one is ignored.

    :param b1:
        First bytes object.
    :param b2:
        Second bytes object.
    :returns:
        Bytes object, result of XOR operation.
    """
    return bytes(x ^ y for x, y in zip(b1, b2))

# -*- coding: utf-8 -*-

import sys

PY33 = sys.version_info >= (3, 3)


if PY33:
    FileNotFoundError = FileNotFoundError
else:
    FileNotFoundError = IOError # cf PEP-3151

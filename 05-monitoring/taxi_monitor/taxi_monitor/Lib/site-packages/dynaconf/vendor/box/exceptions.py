#!/usr/bin/env python
class BoxError(Exception):0
class BoxKeyError(BoxError,KeyError,AttributeError):0
class BoxTypeError(BoxError,TypeError):0
class BoxValueError(BoxError,ValueError):0
class BoxWarning(UserWarning):0
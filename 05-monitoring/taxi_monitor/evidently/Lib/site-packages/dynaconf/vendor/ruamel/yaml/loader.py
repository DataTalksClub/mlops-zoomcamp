from __future__ import absolute_import
_A=None
from.reader import Reader
from.scanner import Scanner,RoundTripScanner
from.parser import Parser,RoundTripParser
from.composer import Composer
from.constructor import BaseConstructor,SafeConstructor,Constructor,RoundTripConstructor
from.resolver import VersionedResolver
if False:from typing import Any,Dict,List,Union,Optional;from.compat import StreamTextType,VersionType
__all__=['BaseLoader','SafeLoader','Loader','RoundTripLoader']
class BaseLoader(Reader,Scanner,Parser,Composer,BaseConstructor,VersionedResolver):
	def __init__(A,stream,version=_A,preserve_quotes=_A):Reader.__init__(A,stream,loader=A);Scanner.__init__(A,loader=A);Parser.__init__(A,loader=A);Composer.__init__(A,loader=A);BaseConstructor.__init__(A,loader=A);VersionedResolver.__init__(A,version,loader=A)
class SafeLoader(Reader,Scanner,Parser,Composer,SafeConstructor,VersionedResolver):
	def __init__(A,stream,version=_A,preserve_quotes=_A):Reader.__init__(A,stream,loader=A);Scanner.__init__(A,loader=A);Parser.__init__(A,loader=A);Composer.__init__(A,loader=A);SafeConstructor.__init__(A,loader=A);VersionedResolver.__init__(A,version,loader=A)
class Loader(Reader,Scanner,Parser,Composer,Constructor,VersionedResolver):
	def __init__(A,stream,version=_A,preserve_quotes=_A):Reader.__init__(A,stream,loader=A);Scanner.__init__(A,loader=A);Parser.__init__(A,loader=A);Composer.__init__(A,loader=A);Constructor.__init__(A,loader=A);VersionedResolver.__init__(A,version,loader=A)
class RoundTripLoader(Reader,RoundTripScanner,RoundTripParser,Composer,RoundTripConstructor,VersionedResolver):
	def __init__(A,stream,version=_A,preserve_quotes=_A):Reader.__init__(A,stream,loader=A);RoundTripScanner.__init__(A,loader=A);RoundTripParser.__init__(A,loader=A);Composer.__init__(A,loader=A);RoundTripConstructor.__init__(A,preserve_quotes=preserve_quotes,loader=A);VersionedResolver.__init__(A,version,loader=A)
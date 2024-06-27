from __future__ import print_function,absolute_import,division,unicode_literals
_B=False
_A=None
from.compat import no_limit_int
from.anchor import Anchor
if _B:from typing import Text,Any,Dict,List
__all__=['ScalarInt','BinaryInt','OctalInt','HexInt','HexCapsInt','DecimalInt']
class ScalarInt(no_limit_int):
	def __new__(D,*E,**A):
		F=A.pop('width',_A);G=A.pop('underscore',_A);C=A.pop('anchor',_A);B=no_limit_int.__new__(D,*E,**A);B._width=F;B._underscore=G
		if C is not _A:B.yaml_set_anchor(C,always_dump=True)
		return B
	def __iadd__(A,a):B=type(A)(A+a);B._width=A._width;B._underscore=A._underscore[:]if A._underscore is not _A else _A;return B
	def __ifloordiv__(A,a):B=type(A)(A//a);B._width=A._width;B._underscore=A._underscore[:]if A._underscore is not _A else _A;return B
	def __imul__(A,a):B=type(A)(A*a);B._width=A._width;B._underscore=A._underscore[:]if A._underscore is not _A else _A;return B
	def __ipow__(A,a):B=type(A)(A**a);B._width=A._width;B._underscore=A._underscore[:]if A._underscore is not _A else _A;return B
	def __isub__(A,a):B=type(A)(A-a);B._width=A._width;B._underscore=A._underscore[:]if A._underscore is not _A else _A;return B
	@property
	def anchor(self):
		A=self
		if not hasattr(A,Anchor.attrib):setattr(A,Anchor.attrib,Anchor())
		return getattr(A,Anchor.attrib)
	def yaml_anchor(A,any=_B):
		if not hasattr(A,Anchor.attrib):return
		if any or A.anchor.always_dump:return A.anchor
	def yaml_set_anchor(A,value,always_dump=_B):A.anchor.value=value;A.anchor.always_dump=always_dump
class BinaryInt(ScalarInt):
	def __new__(A,value,width=_A,underscore=_A,anchor=_A):return ScalarInt.__new__(A,value,width=width,underscore=underscore,anchor=anchor)
class OctalInt(ScalarInt):
	def __new__(A,value,width=_A,underscore=_A,anchor=_A):return ScalarInt.__new__(A,value,width=width,underscore=underscore,anchor=anchor)
class HexInt(ScalarInt):
	def __new__(A,value,width=_A,underscore=_A,anchor=_A):return ScalarInt.__new__(A,value,width=width,underscore=underscore,anchor=anchor)
class HexCapsInt(ScalarInt):
	def __new__(A,value,width=_A,underscore=_A,anchor=_A):return ScalarInt.__new__(A,value,width=width,underscore=underscore,anchor=anchor)
class DecimalInt(ScalarInt):
	def __new__(A,value,width=_A,underscore=_A,anchor=_A):return ScalarInt.__new__(A,value,width=width,underscore=underscore,anchor=anchor)
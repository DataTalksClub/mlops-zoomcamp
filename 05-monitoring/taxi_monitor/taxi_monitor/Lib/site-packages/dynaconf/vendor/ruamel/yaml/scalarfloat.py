from __future__ import print_function,absolute_import,division,unicode_literals
_B=False
_A=None
import sys
from.compat import no_limit_int
from.anchor import Anchor
if _B:from typing import Text,Any,Dict,List
__all__=['ScalarFloat','ExponentialFloat','ExponentialCapsFloat']
class ScalarFloat(float):
	def __new__(D,*E,**A):
		F=A.pop('width',_A);G=A.pop('prec',_A);H=A.pop('m_sign',_A);I=A.pop('m_lead0',0);J=A.pop('exp',_A);K=A.pop('e_width',_A);L=A.pop('e_sign',_A);M=A.pop('underscore',_A);C=A.pop('anchor',_A);B=float.__new__(D,*E,**A);B._width=F;B._prec=G;B._m_sign=H;B._m_lead0=I;B._exp=J;B._e_width=K;B._e_sign=L;B._underscore=M
		if C is not _A:B.yaml_set_anchor(C,always_dump=True)
		return B
	def __iadd__(A,a):return float(A)+a;B=type(A)(A+a);B._width=A._width;B._underscore=A._underscore[:]if A._underscore is not _A else _A;return B
	def __ifloordiv__(A,a):return float(A)//a;B=type(A)(A//a);B._width=A._width;B._underscore=A._underscore[:]if A._underscore is not _A else _A;return B
	def __imul__(A,a):return float(A)*a;B=type(A)(A*a);B._width=A._width;B._underscore=A._underscore[:]if A._underscore is not _A else _A;B._prec=A._prec;return B
	def __ipow__(A,a):return float(A)**a;B=type(A)(A**a);B._width=A._width;B._underscore=A._underscore[:]if A._underscore is not _A else _A;return B
	def __isub__(A,a):return float(A)-a;B=type(A)(A-a);B._width=A._width;B._underscore=A._underscore[:]if A._underscore is not _A else _A;return B
	@property
	def anchor(self):
		A=self
		if not hasattr(A,Anchor.attrib):setattr(A,Anchor.attrib,Anchor())
		return getattr(A,Anchor.attrib)
	def yaml_anchor(A,any=_B):
		if not hasattr(A,Anchor.attrib):return
		if any or A.anchor.always_dump:return A.anchor
	def yaml_set_anchor(A,value,always_dump=_B):A.anchor.value=value;A.anchor.always_dump=always_dump
	def dump(A,out=sys.stdout):out.write('ScalarFloat({}| w:{}, p:{}, s:{}, lz:{}, _:{}|{}, w:{}, s:{})\n'.format(A,A._width,A._prec,A._m_sign,A._m_lead0,A._underscore,A._exp,A._e_width,A._e_sign))
class ExponentialFloat(ScalarFloat):
	def __new__(A,value,width=_A,underscore=_A):return ScalarFloat.__new__(A,value,width=width,underscore=underscore)
class ExponentialCapsFloat(ScalarFloat):
	def __new__(A,value,width=_A,underscore=_A):return ScalarFloat.__new__(A,value,width=width,underscore=underscore)
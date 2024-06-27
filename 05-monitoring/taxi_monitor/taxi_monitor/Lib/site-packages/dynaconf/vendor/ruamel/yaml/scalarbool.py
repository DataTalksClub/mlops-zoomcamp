from __future__ import print_function,absolute_import,division,unicode_literals
_A=False
from.anchor import Anchor
if _A:from typing import Text,Any,Dict,List
__all__=['ScalarBoolean']
class ScalarBoolean(int):
	def __new__(D,*E,**A):
		B=A.pop('anchor',None);C=int.__new__(D,*E,**A)
		if B is not None:C.yaml_set_anchor(B,always_dump=True)
		return C
	@property
	def anchor(self):
		A=self
		if not hasattr(A,Anchor.attrib):setattr(A,Anchor.attrib,Anchor())
		return getattr(A,Anchor.attrib)
	def yaml_anchor(A,any=_A):
		if not hasattr(A,Anchor.attrib):return
		if any or A.anchor.always_dump:return A.anchor
	def yaml_set_anchor(A,value,always_dump=_A):A.anchor.value=value;A.anchor.always_dump=always_dump
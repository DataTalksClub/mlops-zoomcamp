from __future__ import print_function,absolute_import,division,unicode_literals
_C='comment'
_B=False
_A=None
from.compat import text_type
from.anchor import Anchor
if _B:from typing import Text,Any,Dict,List
__all__=['ScalarString','LiteralScalarString','FoldedScalarString','SingleQuotedScalarString','DoubleQuotedScalarString','PlainScalarString','PreservedScalarString']
class ScalarString(text_type):
	__slots__=Anchor.attrib
	def __new__(D,*E,**A):
		B=A.pop('anchor',_A);C=text_type.__new__(D,*E,**A)
		if B is not _A:C.yaml_set_anchor(B,always_dump=True)
		return C
	def replace(A,old,new,maxreplace=-1):return type(A)(text_type.replace(A,old,new,maxreplace))
	@property
	def anchor(self):
		A=self
		if not hasattr(A,Anchor.attrib):setattr(A,Anchor.attrib,Anchor())
		return getattr(A,Anchor.attrib)
	def yaml_anchor(A,any=_B):
		if not hasattr(A,Anchor.attrib):return
		if any or A.anchor.always_dump:return A.anchor
	def yaml_set_anchor(A,value,always_dump=_B):A.anchor.value=value;A.anchor.always_dump=always_dump
class LiteralScalarString(ScalarString):
	__slots__=_C;style='|'
	def __new__(A,value,anchor=_A):return ScalarString.__new__(A,value,anchor=anchor)
PreservedScalarString=LiteralScalarString
class FoldedScalarString(ScalarString):
	__slots__='fold_pos',_C;style='>'
	def __new__(A,value,anchor=_A):return ScalarString.__new__(A,value,anchor=anchor)
class SingleQuotedScalarString(ScalarString):
	__slots__=();style="'"
	def __new__(A,value,anchor=_A):return ScalarString.__new__(A,value,anchor=anchor)
class DoubleQuotedScalarString(ScalarString):
	__slots__=();style='"'
	def __new__(A,value,anchor=_A):return ScalarString.__new__(A,value,anchor=anchor)
class PlainScalarString(ScalarString):
	__slots__=();style=''
	def __new__(A,value,anchor=_A):return ScalarString.__new__(A,value,anchor=anchor)
def preserve_literal(s):return LiteralScalarString(s.replace('\r\n','\n').replace('\r','\n'))
def walk_tree(base,map=_A):
	A=base;from dynaconf.vendor.ruamel.yaml.compat import string_types as E,MutableMapping as G,MutableSequence as H
	if map is _A:map={'\n':preserve_literal}
	if isinstance(A,G):
		for F in A:
			C=A[F]
			if isinstance(C,E):
				for B in map:
					if B in C:A[F]=map[B](C);break
			else:walk_tree(C)
	elif isinstance(A,H):
		for(I,D)in enumerate(A):
			if isinstance(D,E):
				for B in map:
					if B in D:A[I]=map[B](D);break
			else:walk_tree(D)
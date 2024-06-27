from __future__ import absolute_import,print_function
_A='lazy_self'
from functools import partial
import re
from.compat import text_type,binary_type
if False:from typing import Any,Dict,Optional,List,Text;from.compat import StreamTextType
class LazyEval:
	def __init__(A,func,*C,**D):
		def B():B=func(*C,**D);object.__setattr__(A,_A,lambda:B);return B
		object.__setattr__(A,_A,B)
	def __getattribute__(B,name):
		A=object.__getattribute__(B,_A)
		if name==_A:return A
		return getattr(A(),name)
	def __setattr__(A,name,value):setattr(A.lazy_self(),name,value)
RegExp=partial(LazyEval,re.compile)
def load_yaml_guess_indent(stream,**N):
	D=stream;B=None;from.main import round_trip_load as O
	def K(l):
		A=0
		while A<len(l)and l[A]==' ':A+=1
		return A
	if isinstance(D,text_type):F=D
	elif isinstance(D,binary_type):F=D.decode('utf-8')
	else:F=D.read()
	G=B;H=B;L=B;E=B;I=0
	for C in F.splitlines():
		J=C.rstrip();P=J.lstrip()
		if P.startswith('- '):
			M=K(C);L=M-I;A=M+1
			while C[A]==' ':A+=1
			if C[A]=='#':continue
			H=A-I;break
		if G is B and E is not B and J:
			A=0
			while C[A]in' -':A+=1
			if A>E:G=A-E
		if J.endswith(':'):
			I=K(C);A=0
			while C[A]==' ':A+=1
			E=A;continue
		E=B
	if H is B and G is not B:H=G
	return O(F,**N),H,L
def configobj_walker(cfg):
	B=cfg;from configobj import ConfigObj as D;assert isinstance(B,D)
	for A in B.initial_comment:
		if A.strip():yield A
	for C in _walk_section(B):
		if C.strip():yield C
	for A in B.final_comment:
		if A.strip():yield A
def _walk_section(s,level=0):
	H=level;G="'";F='\n';from configobj import Section as J;assert isinstance(s,J);D='  '*H
	for A in s.scalars:
		for B in s.comments[A]:yield D+B.strip()
		C=s[A]
		if F in C:I=D+'  ';C='|\n'+I+C.strip().replace(F,F+I)
		elif':'in C:C=G+C.replace(G,"''")+G
		E='{0}{1}: {2}'.format(D,A,C);B=s.inline_comments[A]
		if B:E+=' '+B
		yield E
	for A in s.sections:
		for B in s.comments[A]:yield D+B.strip()
		E='{0}{1}:'.format(D,A);B=s.inline_comments[A]
		if B:E+=' '+B
		yield E
		for K in _walk_section(s[A],level=H+1):yield K
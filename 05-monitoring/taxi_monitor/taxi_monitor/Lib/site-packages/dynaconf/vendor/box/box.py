#!/usr/bin/env python
_W='box_settings'
_V='default_box_attr'
_U='Box is frozen'
_T='modify_tuples_box'
_S='box_safe_prefix'
_R='default_box_none_transform'
_Q='__created'
_P='box_dots'
_O='box_duplicates'
_N='ignore'
_M='strict'
_L='box_recast'
_K='box_intact_types'
_J='default_box'
_I='utf-8'
_H='_box_config'
_G=True
_F='camel_killer_box'
_E='conversion_box'
_D='frozen_box'
_C='__safe_keys'
_B=False
_A=None
import copy,re,string,warnings
from collections.abc import Iterable,Mapping,Callable
from keyword import kwlist
from pathlib import Path
from typing import Any,Union,Tuple,List,Dict
from dynaconf.vendor import box
from.converters import _to_json,_from_json,_from_toml,_to_toml,_from_yaml,_to_yaml,BOX_PARAMETERS
from.exceptions import BoxError,BoxKeyError,BoxTypeError,BoxValueError,BoxWarning
__all__=['Box']
_first_cap_re=re.compile('(.)([A-Z][a-z]+)')
_all_cap_re=re.compile('([a-z0-9])([A-Z])')
_list_pos_re=re.compile('\\[(\\d+)\\]')
NO_DEFAULT=object()
def _camel_killer(attr):B='\\1_\\2';A=attr;A=str(A);C=_first_cap_re.sub(B,A);D=_all_cap_re.sub(B,C);return re.sub(' *_+','_',D.lower())
def _recursive_tuples(iterable,box_class,recreate_tuples=_B,**E):
	D=recreate_tuples;C=box_class;B=[]
	for A in iterable:
		if isinstance(A,dict):B.append(C(A,**E))
		elif isinstance(A,list)or D and isinstance(A,tuple):B.append(_recursive_tuples(A,C,D,**E))
		else:B.append(A)
	return tuple(B)
def _parse_box_dots(item):
	A=item
	for(B,C)in enumerate(A):
		if C=='[':return A[:B],A[B:]
		elif C=='.':return A[:B],A[B+1:]
	raise BoxError('Could not split box dots properly')
def _get_box_config():return{_Q:_B,_C:{}}
class Box(dict):
	_protected_keys=['to_dict','to_json','to_yaml','from_yaml','from_json','from_toml','to_toml','merge_update']+[A for A in dir({})if not A.startswith('_')]
	def __new__(A,*D,box_settings=_A,default_box=_B,default_box_attr=NO_DEFAULT,default_box_none_transform=_G,frozen_box=_B,camel_killer_box=_B,conversion_box=_G,modify_tuples_box=_B,box_safe_prefix='x',box_duplicates=_N,box_intact_types=(),box_recast=_A,box_dots=_B,**E):C=default_box_attr;B=super(Box,A).__new__(A,*D,**E);B._box_config=_get_box_config();B._box_config.update({_J:default_box,_V:A.__class__ if C is NO_DEFAULT else C,_R:default_box_none_transform,_E:conversion_box,_S:box_safe_prefix,_D:frozen_box,_F:camel_killer_box,_T:modify_tuples_box,_O:box_duplicates,_K:tuple(box_intact_types),_L:box_recast,_P:box_dots,_W:box_settings or{}});return B
	def __init__(A,*B,box_settings=_A,default_box=_B,default_box_attr=NO_DEFAULT,default_box_none_transform=_G,frozen_box=_B,camel_killer_box=_B,conversion_box=_G,modify_tuples_box=_B,box_safe_prefix='x',box_duplicates=_N,box_intact_types=(),box_recast=_A,box_dots=_B,**F):
		E=default_box_attr;super().__init__();A._box_config=_get_box_config();A._box_config.update({_J:default_box,_V:A.__class__ if E is NO_DEFAULT else E,_R:default_box_none_transform,_E:conversion_box,_S:box_safe_prefix,_D:frozen_box,_F:camel_killer_box,_T:modify_tuples_box,_O:box_duplicates,_K:tuple(box_intact_types),_L:box_recast,_P:box_dots,_W:box_settings or{}})
		if not A._box_config[_E]and A._box_config[_O]!=_N:raise BoxError('box_duplicates are only for conversion_boxes')
		if len(B)==1:
			if isinstance(B[0],str):raise BoxValueError('Cannot extrapolate Box from string')
			if isinstance(B[0],Mapping):
				for(D,C)in B[0].items():
					if C is B[0]:C=A
					if C is _A and A._box_config[_J]and A._box_config[_R]:continue
					A.__setitem__(D,C)
			elif isinstance(B[0],Iterable):
				for(D,C)in B[0]:A.__setitem__(D,C)
			else:raise BoxValueError('First argument must be mapping or iterable')
		elif B:raise BoxTypeError(f"Box expected at most 1 argument, got {len(B)}")
		for(D,C)in F.items():
			if B and isinstance(B[0],Mapping)and C is B[0]:C=A
			A.__setitem__(D,C)
		A._box_config[_Q]=_G
	def __add__(C,other):
		A=other;B=C.copy()
		if not isinstance(A,dict):raise BoxTypeError(f"Box can only merge two boxes or a box and a dictionary.")
		B.merge_update(A);return B
	def __hash__(A):
		if A._box_config[_D]:
			B=54321
			for C in A.items():B^=hash(C)
			return B
		raise BoxTypeError('unhashable type: "Box"')
	def __dir__(B):
		D=string.ascii_letters+string.digits+'_';C=set(super().__dir__())
		for A in B.keys():
			A=str(A)
			if' 'not in A and A[0]not in string.digits and A not in kwlist:
				for E in A:
					if E not in D:break
				else:C.add(A)
		for A in B.keys():
			if A not in C:
				if B._box_config[_E]:
					A=B._safe_attr(A)
					if A:C.add(A)
		return list(C)
	def get(B,key,default=NO_DEFAULT):
		C=key;A=default
		if C not in B:
			if A is NO_DEFAULT:
				if B._box_config[_J]and B._box_config[_R]:return B.__get_default(C)
				else:return
			if isinstance(A,dict)and not isinstance(A,Box):return Box(A,box_settings=B._box_config.get(_W))
			if isinstance(A,list)and not isinstance(A,box.BoxList):return box.BoxList(A)
			return A
		return B[C]
	def copy(A):return Box(super().copy(),**A.__box_config())
	def __copy__(A):return Box(super().copy(),**A.__box_config())
	def __deepcopy__(A,memodict=_A):
		B=memodict;E=A._box_config[_D];D=A.__box_config();D[_D]=_B;C=A.__class__(**D);B=B or{};B[id(A)]=C
		for(F,G)in A.items():C[copy.deepcopy(F,B)]=copy.deepcopy(G,B)
		C._box_config[_D]=E;return C
	def __setstate__(A,state):B=state;A._box_config=B[_H];A.__dict__.update(B)
	def keys(A):return super().keys()
	def values(A):return[A[B]for B in A.keys()]
	def items(A):return[(B,A[B])for B in A.keys()]
	def _safe_items(A):return[(B,A._safe_get(B))for B in A.keys()]
	def __get_default(B,item):
		A=B._box_config[_V]
		if A in(B.__class__,dict):C=B.__class__(**B.__box_config())
		elif isinstance(A,dict):C=B.__class__(**B.__box_config(),**A)
		elif isinstance(A,list):C=box.BoxList(**B.__box_config())
		elif isinstance(A,Callable):C=A()
		elif hasattr(A,'copy'):C=A.copy()
		else:C=A
		B.__convert_and_store(item,C);return C
	def __box_config(C):
		A={}
		for(B,D)in C._box_config.copy().items():
			if not B.startswith('__'):A[B]=D
		return A
	def __recast(A,item,value):
		C=value;B=item
		if A._box_config[_L]and B in A._box_config[_L]:
			try:return A._box_config[_L][B](C)
			except ValueError:raise BoxValueError(f"Cannot convert {C} to {A._box_config[_L][B]}")from _A
		return C
	def __convert_and_store(B,item,value):
		C=item;A=value
		if B._box_config[_E]:D=B._safe_attr(C);B._box_config[_C][D]=C
		if isinstance(A,(int,float,str,bytes,bytearray,bool,complex,set,frozenset)):return super().__setitem__(C,A)
		if B._box_config[_K]and isinstance(A,B._box_config[_K]):return super().__setitem__(C,A)
		if isinstance(A,dict)and not isinstance(A,Box):A=B.__class__(A,**B.__box_config())
		elif isinstance(A,list)and not isinstance(A,box.BoxList):
			if B._box_config[_D]:A=_recursive_tuples(A,B.__class__,recreate_tuples=B._box_config[_T],**B.__box_config())
			else:A=box.BoxList(A,box_class=B.__class__,**B.__box_config())
		elif B._box_config[_T]and isinstance(A,tuple):A=_recursive_tuples(A,B.__class__,recreate_tuples=_G,**B.__box_config())
		super().__setitem__(C,A)
	def __getitem__(B,item,_ignore_default=_B):
		A=item
		try:return super().__getitem__(A)
		except KeyError as E:
			if A==_H:raise BoxKeyError('_box_config should only exist as an attribute and is never defaulted')from _A
			if B._box_config[_P]and isinstance(A,str)and('.'in A or'['in A):
				C,F=_parse_box_dots(A)
				if C in B.keys():
					if hasattr(B[C],'__getitem__'):return B[C][F]
			if B._box_config[_F]and isinstance(A,str):
				D=_camel_killer(A)
				if D in B.keys():return super().__getitem__(D)
			if B._box_config[_J]and not _ignore_default:return B.__get_default(A)
			raise BoxKeyError(str(E))from _A
	def __getattr__(A,item):
		B=item
		try:
			try:C=A.__getitem__(B,_ignore_default=_G)
			except KeyError:C=object.__getattribute__(A,B)
		except AttributeError as E:
			if B=='__getstate__':raise BoxKeyError(B)from _A
			if B==_H:raise BoxError('_box_config key must exist')from _A
			if A._box_config[_E]:
				D=A._safe_attr(B)
				if D in A._box_config[_C]:return A.__getitem__(A._box_config[_C][D])
			if A._box_config[_J]:return A.__get_default(B)
			raise BoxKeyError(str(E))from _A
		return C
	def __setitem__(A,key,value):
		C=value;B=key
		if B!=_H and A._box_config[_Q]and A._box_config[_D]:raise BoxError(_U)
		if A._box_config[_P]and isinstance(B,str)and'.'in B:
			D,E=_parse_box_dots(B)
			if D in A.keys():
				if hasattr(A[D],'__setitem__'):return A[D].__setitem__(E,C)
		C=A.__recast(B,C)
		if B not in A.keys()and A._box_config[_F]:
			if A._box_config[_F]and isinstance(B,str):B=_camel_killer(B)
		if A._box_config[_E]and A._box_config[_O]!=_N:A._conversion_checks(B)
		A.__convert_and_store(B,C)
	def __setattr__(A,key,value):
		C=value;B=key
		if B!=_H and A._box_config[_D]and A._box_config[_Q]:raise BoxError(_U)
		if B in A._protected_keys:raise BoxKeyError(f'Key name "{B}" is protected')
		if B==_H:return object.__setattr__(A,B,C)
		C=A.__recast(B,C);D=A._safe_attr(B)
		if D in A._box_config[_C]:B=A._box_config[_C][D]
		A.__setitem__(B,C)
	def __delitem__(A,key):
		B=key
		if A._box_config[_D]:raise BoxError(_U)
		if B not in A.keys()and A._box_config[_P]and isinstance(B,str)and'.'in B:
			C,E=B.split('.',1)
			if C in A.keys()and isinstance(A[C],dict):return A[C].__delitem__(E)
		if B not in A.keys()and A._box_config[_F]:
			if A._box_config[_F]and isinstance(B,str):
				for D in A:
					if _camel_killer(B)==D:B=D;break
		super().__delitem__(B)
	def __delattr__(A,item):
		B=item
		if A._box_config[_D]:raise BoxError(_U)
		if B==_H:raise BoxError('"_box_config" is protected')
		if B in A._protected_keys:raise BoxKeyError(f'Key name "{B}" is protected')
		try:A.__delitem__(B)
		except KeyError as D:
			if A._box_config[_E]:
				C=A._safe_attr(B)
				if C in A._box_config[_C]:A.__delitem__(A._box_config[_C][C]);del A._box_config[_C][C];return
			raise BoxKeyError(D)
	def pop(B,key,*C):
		A=key
		if C:
			if len(C)!=1:raise BoxError('pop() takes only one optional argument "default"')
			try:D=B[A]
			except KeyError:return C[0]
			else:del B[A];return D
		try:D=B[A]
		except KeyError:raise BoxKeyError('{0}'.format(A))from _A
		else:del B[A];return D
	def clear(A):super().clear();A._box_config[_C].clear()
	def popitem(A):
		try:B=next(A.__iter__())
		except StopIteration:raise BoxKeyError('Empty box')from _A
		return B,A.pop(B)
	def __repr__(A):return f"<Box: {A.to_dict()}>"
	def __str__(A):return str(A.to_dict())
	def __iter__(A):
		for B in A.keys():yield B
	def __reversed__(A):
		for B in reversed(list(A.keys())):yield B
	def to_dict(D):
		A=dict(D)
		for(C,B)in A.items():
			if B is D:A[C]=A
			elif isinstance(B,Box):A[C]=B.to_dict()
			elif isinstance(B,box.BoxList):A[C]=B.to_list()
		return A
	def update(C,__m=_A,**D):
		B=__m
		if B:
			if hasattr(B,'keys'):
				for A in B:C.__convert_and_store(A,B[A])
			else:
				for(A,E)in B:C.__convert_and_store(A,E)
		for A in D:C.__convert_and_store(A,D[A])
	def merge_update(A,__m=_A,**E):
		C=__m
		def D(k,v):
			B=A._box_config[_K]and isinstance(v,A._box_config[_K])
			if isinstance(v,dict)and not B:
				v=A.__class__(v,**A.__box_config())
				if k in A and isinstance(A[k],dict):
					if isinstance(A[k],Box):A[k].merge_update(v)
					else:A[k].update(v)
					return
			if isinstance(v,list)and not B:v=box.BoxList(v,**A.__box_config())
			A.__setitem__(k,v)
		if C:
			if hasattr(C,'keys'):
				for B in C:D(B,C[B])
			else:
				for(B,F)in C:D(B,F)
		for B in E:D(B,E[B])
	def setdefault(B,item,default=_A):
		C=item;A=default
		if C in B:return B[C]
		if isinstance(A,dict):A=B.__class__(A,**B.__box_config())
		if isinstance(A,list):A=box.BoxList(A,box_class=B.__class__,**B.__box_config())
		B[C]=A;return A
	def _safe_attr(C,attr):
		B=attr;G=string.ascii_letters+string.digits+'_'
		if isinstance(B,tuple):B='_'.join([str(A)for A in B])
		B=B.decode(_I,_N)if isinstance(B,bytes)else str(B)
		if C.__box_config()[_F]:B=_camel_killer(B)
		A=[];D=0
		for(E,F)in enumerate(B):
			if F in G:D=E;A.append(F)
			elif not A:continue
			elif D==E-1:A.append('_')
		A=''.join(A)[:D+1]
		try:int(A[0])
		except(ValueError,IndexError):pass
		else:A=f"{C.__box_config()[_S]}{A}"
		if A in kwlist:A=f"{C.__box_config()[_S]}{A}"
		return A
	def _conversion_checks(A,item):
		B=A._safe_attr(item)
		if B in A._box_config[_C]:
			C=[f"{item}({B})",f"{A._box_config[_C][B]}({B})"]
			if A._box_config[_O].startswith('warn'):warnings.warn(f"Duplicate conversion attributes exist: {C}",BoxWarning)
			else:raise BoxError(f"Duplicate conversion attributes exist: {C}")
	def to_json(A,filename=_A,encoding=_I,errors=_M,**B):return _to_json(A.to_dict(),filename=filename,encoding=encoding,errors=errors,**B)
	@classmethod
	def from_json(E,json_string=_A,filename=_A,encoding=_I,errors=_M,**A):
		D={}
		for B in A.copy():
			if B in BOX_PARAMETERS:D[B]=A.pop(B)
		C=_from_json(json_string,filename=filename,encoding=encoding,errors=errors,**A)
		if not isinstance(C,dict):raise BoxError(f"json data not returned as a dictionary, but rather a {type(C).__name__}")
		return E(C,**D)
	def to_yaml(A,filename=_A,default_flow_style=_B,encoding=_I,errors=_M,**B):return _to_yaml(A.to_dict(),filename=filename,default_flow_style=default_flow_style,encoding=encoding,errors=errors,**B)
	@classmethod
	def from_yaml(E,yaml_string=_A,filename=_A,encoding=_I,errors=_M,**A):
		D={}
		for B in A.copy():
			if B in BOX_PARAMETERS:D[B]=A.pop(B)
		C=_from_yaml(yaml_string=yaml_string,filename=filename,encoding=encoding,errors=errors,**A)
		if not isinstance(C,dict):raise BoxError(f"yaml data not returned as a dictionary but rather a {type(C).__name__}")
		return E(C,**D)
	def to_toml(A,filename=_A,encoding=_I,errors=_M):return _to_toml(A.to_dict(),filename=filename,encoding=encoding,errors=errors)
	@classmethod
	def from_toml(D,toml_string=_A,filename=_A,encoding=_I,errors=_M,**B):
		C={}
		for A in B.copy():
			if A in BOX_PARAMETERS:C[A]=B.pop(A)
		E=_from_toml(toml_string=toml_string,filename=filename,encoding=encoding,errors=errors);return D(E,**C)
#!/usr/bin/env python
_G='box_dots'
_F='BoxList is frozen'
_E='frozen_box'
_D=False
_C='strict'
_B='utf-8'
_A=None
import copy,re
from typing import Iterable,Optional
from dynaconf.vendor import box
from.converters import _to_yaml,_from_yaml,_to_json,_from_json,_to_toml,_from_toml,_to_csv,_from_csv,BOX_PARAMETERS
from.exceptions import BoxError,BoxTypeError,BoxKeyError
_list_pos_re=re.compile('\\[(\\d+)\\]')
DYNABOX_CLASS=_A
def get_dynabox_class_avoiding_circular_import():
	global DYNABOX_CLASS
	if DYNABOX_CLASS is _A:from dynaconf.utils.boxing import DynaBox as A;DYNABOX_CLASS=A
	return DYNABOX_CLASS
class BoxList(list):
	def __init__(A,iterable=_A,box_class=_A,**C):
		B=iterable;A.box_class=box_class or get_dynabox_class_avoiding_circular_import();A.box_options=C;A.box_org_ref=A.box_org_ref=id(B)if B else 0
		if B:
			for D in B:A.append(D)
		if C.get(_E):
			def E(*A,**B):raise BoxError(_F)
			for F in['append','extend','insert','pop','remove','reverse','sort']:A.__setattr__(F,E)
	def __getitem__(B,item):
		A=item
		if B.box_options.get(_G)and isinstance(A,str)and A.startswith('['):
			C=_list_pos_re.search(A);D=super(BoxList,B).__getitem__(int(C.groups()[0]))
			if len(C.group())==len(A):return D
			return D.__getitem__(A[len(C.group()):].lstrip('.'))
		return super(BoxList,B).__getitem__(A)
	def __delitem__(A,key):
		if A.box_options.get(_E):raise BoxError(_F)
		super(BoxList,A).__delitem__(key)
	def __setitem__(B,key,value):
		C=value;A=key
		if B.box_options.get(_E):raise BoxError(_F)
		if B.box_options.get(_G)and isinstance(A,str)and A.startswith('['):
			D=_list_pos_re.search(A);E=int(D.groups()[0])
			if len(D.group())==len(A):return super(BoxList,B).__setitem__(E,C)
			return super(BoxList,B).__getitem__(E).__setitem__(A[len(D.group()):].lstrip('.'),C)
		super(BoxList,B).__setitem__(A,C)
	def _is_intact_type(A,obj):
		B='box_intact_types'
		try:
			if A.box_options.get(B)and isinstance(obj,A.box_options[B]):return True
		except AttributeError as C:
			if'box_options'in A.__dict__:raise BoxKeyError(C)
		return _D
	def append(A,p_object):
		B=p_object
		if isinstance(B,dict)and not A._is_intact_type(B):
			try:B=A.box_class(B,**A.box_options)
			except AttributeError as C:
				if'box_class'in A.__dict__:raise BoxKeyError(C)
		elif isinstance(B,list)and not A._is_intact_type(B):
			try:B=A if id(B)==A.box_org_ref else BoxList(B,**A.box_options)
			except AttributeError as C:
				if'box_org_ref'in A.__dict__:raise BoxKeyError(C)
		super(BoxList,A).append(B)
	def extend(A,iterable):
		for B in iterable:A.append(B)
	def insert(B,index,p_object):
		A=p_object
		if isinstance(A,dict)and not B._is_intact_type(A):A=B.box_class(A,**B.box_options)
		elif isinstance(A,list)and not B._is_intact_type(A):A=B if id(A)==B.box_org_ref else BoxList(A)
		super(BoxList,B).insert(index,A)
	def __repr__(A):return f"<BoxList: {A.to_list()}>"
	def __str__(A):return str(A.to_list())
	def __copy__(A):return BoxList((A for A in A),A.box_class,**A.box_options)
	def __deepcopy__(B,memo=_A):
		A=memo;C=B.__class__();A=A or{};A[id(B)]=C
		for D in B:C.append(copy.deepcopy(D,memo=A))
		return C
	def __hash__(A):
		if A.box_options.get(_E):B=98765;B^=hash(tuple(A));return B
		raise BoxTypeError("unhashable type: 'BoxList'")
	def to_list(C):
		A=[]
		for B in C:
			if B is C:A.append(A)
			elif isinstance(B,box.Box):A.append(B.to_dict())
			elif isinstance(B,BoxList):A.append(B.to_list())
			else:A.append(B)
		return A
	def to_json(D,filename=_A,encoding=_B,errors=_C,multiline=_D,**E):
		C=errors;B=encoding;A=filename
		if A and multiline:
			F=[_to_json(A,filename=_D,encoding=B,errors=C,**E)for A in D]
			with open(A,'w',encoding=B,errors=C)as G:G.write('\n'.join(F))
		else:return _to_json(D.to_list(),filename=A,encoding=B,errors=C,**E)
	@classmethod
	def from_json(E,json_string=_A,filename=_A,encoding=_B,errors=_C,multiline=_D,**A):
		D={}
		for B in list(A.keys()):
			if B in BOX_PARAMETERS:D[B]=A.pop(B)
		C=_from_json(json_string,filename=filename,encoding=encoding,errors=errors,multiline=multiline,**A)
		if not isinstance(C,list):raise BoxError(f"json data not returned as a list, but rather a {type(C).__name__}")
		return E(C,**D)
	def to_yaml(A,filename=_A,default_flow_style=_D,encoding=_B,errors=_C,**B):return _to_yaml(A.to_list(),filename=filename,default_flow_style=default_flow_style,encoding=encoding,errors=errors,**B)
	@classmethod
	def from_yaml(E,yaml_string=_A,filename=_A,encoding=_B,errors=_C,**A):
		D={}
		for B in list(A.keys()):
			if B in BOX_PARAMETERS:D[B]=A.pop(B)
		C=_from_yaml(yaml_string=yaml_string,filename=filename,encoding=encoding,errors=errors,**A)
		if not isinstance(C,list):raise BoxError(f"yaml data not returned as a list but rather a {type(C).__name__}")
		return E(C,**D)
	def to_toml(A,filename=_A,key_name='toml',encoding=_B,errors=_C):return _to_toml({key_name:A.to_list()},filename=filename,encoding=encoding,errors=errors)
	@classmethod
	def from_toml(F,toml_string=_A,filename=_A,key_name='toml',encoding=_B,errors=_C,**C):
		A=key_name;D={}
		for B in list(C.keys()):
			if B in BOX_PARAMETERS:D[B]=C.pop(B)
		E=_from_toml(toml_string=toml_string,filename=filename,encoding=encoding,errors=errors)
		if A not in E:raise BoxError(f"{A} was not found.")
		return F(E[A],**D)
	def to_csv(A,filename,encoding=_B,errors=_C):_to_csv(A,filename=filename,encoding=encoding,errors=errors)
	@classmethod
	def from_csv(A,filename,encoding=_B,errors=_C):return A(_from_csv(filename=filename,encoding=encoding,errors=errors))
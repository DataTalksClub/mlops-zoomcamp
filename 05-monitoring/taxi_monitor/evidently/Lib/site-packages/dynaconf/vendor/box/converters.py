#!/usr/bin/env python
_E=False
_D=True
_C='strict'
_B='utf-8'
_A=None
import csv,json,sys,warnings
from pathlib import Path
import dynaconf.vendor.ruamel.yaml as yaml
from dynaconf.vendor.box.exceptions import BoxError,BoxWarning
from dynaconf.vendor import tomllib as toml
BOX_PARAMETERS='default_box','default_box_attr','conversion_box','frozen_box','camel_killer_box','box_safe_prefix','box_duplicates','ordered_box','default_box_none_transform','box_dots','modify_tuples_box','box_intact_types','box_recast'
def _exists(filename,create=_E):
	A=filename;B=Path(A)
	if create:
		try:B.touch(exist_ok=_D)
		except OSError as C:raise BoxError(f"Could not create file {A} - {C}")
		else:return
	if not B.exists():raise BoxError(f'File "{A}" does not exist')
	if not B.is_file():raise BoxError(f"{A} is not a file")
def _to_json(obj,filename=_A,encoding=_B,errors=_C,**C):
	A=filename;B=json.dumps(obj,ensure_ascii=_E,**C)
	if A:
		_exists(A,create=_D)
		with open(A,'w',encoding=encoding,errors=errors)as D:D.write(B if sys.version_info>=(3,0)else B.decode(_B))
	else:return B
def _from_json(json_string=_A,filename=_A,encoding=_B,errors=_C,multiline=_E,**B):
	D=json_string;A=filename
	if A:
		_exists(A)
		with open(A,'r',encoding=encoding,errors=errors)as E:
			if multiline:C=[json.loads(A.strip(),**B)for A in E if A.strip()and not A.strip().startswith('#')]
			else:C=json.load(E,**B)
	elif D:C=json.loads(D,**B)
	else:raise BoxError('from_json requires a string or filename')
	return C
def _to_yaml(obj,filename=_A,default_flow_style=_E,encoding=_B,errors=_C,**C):
	B=default_flow_style;A=filename
	if A:
		_exists(A,create=_D)
		with open(A,'w',encoding=encoding,errors=errors)as D:yaml.dump(obj,stream=D,default_flow_style=B,**C)
	else:return yaml.dump(obj,default_flow_style=B,**C)
def _from_yaml(yaml_string=_A,filename=_A,encoding=_B,errors=_C,**A):
	E='Loader';C=yaml_string;B=filename
	if E not in A:A[E]=yaml.SafeLoader
	if B:
		_exists(B)
		with open(B,'r',encoding=encoding,errors=errors)as F:D=yaml.load(F,**A)
	elif C:D=yaml.load(C,**A)
	else:raise BoxError('from_yaml requires a string or filename')
	return D
def _to_toml(obj,filename=_A,encoding=_B,errors=_C):
	A=filename
	if A:
		_exists(A,create=_D)
		with open(A,'w',encoding=encoding,errors=errors)as B:toml.dump(obj,B)
	else:return toml.dumps(obj)
def _from_toml(toml_string=_A,filename=_A,encoding=_B,errors=_C):
	B=toml_string;A=filename
	if A:
		_exists(A)
		with open(A,'r',encoding=encoding,errors=errors)as D:C=toml.load(D)
	elif B:C=toml.loads(B)
	else:raise BoxError('from_toml requires a string or filename')
	return C
def _to_csv(box_list,filename,encoding=_B,errors=_C):
	B=filename;A=box_list;C=list(A[0].keys())
	for E in A:
		if list(E.keys())!=C:raise BoxError('BoxList must contain the same dictionary structure for every item to convert to csv')
	if B:
		_exists(B,create=_D)
		with open(B,'w',encoding=encoding,errors=errors,newline='')as F:
			D=csv.DictWriter(F,fieldnames=C);D.writeheader()
			for G in A:D.writerow(G)
def _from_csv(filename,encoding=_B,errors=_C):
	A=filename;_exists(A)
	with open(A,'r',encoding=encoding,errors=errors,newline='')as B:C=csv.DictReader(B);return[A for A in C]
#!/usr/bin/env python
from json import JSONDecodeError
from pathlib import Path
from typing import Union
from dynaconf.vendor.tomllib import TOMLDecodeError
from dynaconf.vendor.ruamel.yaml import YAMLError
from.exceptions import BoxError
from.box import Box
from.box_list import BoxList
__all__=['box_from_file']
def _to_json(data):
	try:return Box.from_json(data)
	except JSONDecodeError:raise BoxError('File is not JSON as expected')
	except BoxError:return BoxList.from_json(data)
def _to_yaml(data):
	try:return Box.from_yaml(data)
	except YAMLError:raise BoxError('File is not YAML as expected')
	except BoxError:return BoxList.from_yaml(data)
def _to_toml(data):
	try:return Box.from_toml(data)
	except TOMLDecodeError:raise BoxError('File is not TOML as expected')
def box_from_file(file,file_type=None,encoding='utf-8',errors='strict'):
	C=file_type;A=file
	if not isinstance(A,Path):A=Path(A)
	if not A.exists():raise BoxError(f'file "{A}" does not exist')
	B=A.read_text(encoding=encoding,errors=errors)
	if C:
		if C.lower()=='json':return _to_json(B)
		if C.lower()=='yaml':return _to_yaml(B)
		if C.lower()=='toml':return _to_toml(B)
		raise BoxError(f'"{C}" is an unknown type, please use either toml, yaml or json')
	if A.suffix in('.json','.jsn'):return _to_json(B)
	if A.suffix in('.yaml','.yml'):return _to_yaml(B)
	if A.suffix in('.tml','.toml'):return _to_toml(B)
	raise BoxError(f"Could not determine file type based off extension, please provide file_type")
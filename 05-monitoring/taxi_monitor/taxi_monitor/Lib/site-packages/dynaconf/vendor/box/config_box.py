#!/usr/bin/env python
_D='getint'
_C='getfloat'
_B='getboolean'
_A=None
from dynaconf.vendor.box.box import Box
class ConfigBox(Box):
	_protected_keys=dir(Box)+['bool','int','float','list',_B,_C,_D]
	def __getattr__(A,item):
		try:return super().__getattr__(item)
		except AttributeError:return super().__getattr__(item.lower())
	def __dir__(A):return super().__dir__()+['bool','int','float','list',_B,_C,_D]
	def bool(D,item,default=_A):
		C=False;B=default;A=item
		try:A=D.__getattr__(A)
		except AttributeError as E:
			if B is not _A:return B
			raise E
		if isinstance(A,(bool,int)):return bool(A)
		if isinstance(A,str)and A.lower()in('n','no','false','f','0'):return C
		return True if A else C
	def int(C,item,default=_A):
		B=default;A=item
		try:A=C.__getattr__(A)
		except AttributeError as D:
			if B is not _A:return B
			raise D
		return int(A)
	def float(C,item,default=_A):
		B=default;A=item
		try:A=C.__getattr__(A)
		except AttributeError as D:
			if B is not _A:return B
			raise D
		return float(A)
	def list(E,item,default=_A,spliter=',',strip=True,mod=_A):
		C=strip;B=default;A=item
		try:A=E.__getattr__(A)
		except AttributeError as F:
			if B is not _A:return B
			raise F
		if C:A=A.lstrip('[').rstrip(']')
		D=[A.strip()if C else A for A in A.split(spliter)]
		if mod:return list(map(mod,D))
		return D
	def getboolean(A,item,default=_A):return A.bool(item,default)
	def getint(A,item,default=_A):return A.int(item,default)
	def getfloat(A,item,default=_A):return A.float(item,default)
	def __repr__(A):return'<ConfigBox: {0}>'.format(str(A.to_dict()))
	def copy(A):return ConfigBox(super().copy())
	def __copy__(A):return ConfigBox(super().copy())
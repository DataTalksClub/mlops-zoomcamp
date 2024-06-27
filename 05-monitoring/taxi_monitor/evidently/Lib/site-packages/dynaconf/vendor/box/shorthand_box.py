#!/usr/bin/env python
from dynaconf.vendor.box.box import Box
class SBox(Box):
	_protected_keys=dir({})+['to_dict','to_json','to_yaml','json','yaml','from_yaml','from_json','dict','toml','from_toml','to_toml']
	@property
	def dict(self):return self.to_dict()
	@property
	def json(self):return self.to_json()
	@property
	def yaml(self):return self.to_yaml()
	@property
	def toml(self):return self.to_toml()
	def __repr__(A):return'<ShorthandBox: {0}>'.format(str(A.to_dict()))
	def copy(A):return SBox(super(SBox,A).copy())
	def __copy__(A):return SBox(super(SBox,A).copy())
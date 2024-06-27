if False:from typing import Any,Dict,Optional,List,Union,Optional,Iterator
anchor_attrib='_yaml_anchor'
class Anchor:
	__slots__='value','always_dump';attrib=anchor_attrib
	def __init__(A):A.value=None;A.always_dump=False
	def __repr__(A):B=', (always dump)'if A.always_dump else'';return'Anchor({!r}{})'.format(A.value,B)
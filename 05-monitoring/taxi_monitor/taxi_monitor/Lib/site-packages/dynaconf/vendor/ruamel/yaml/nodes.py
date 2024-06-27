from __future__ import print_function
_A=None
import sys
from.compat import string_types
if False:from typing import Dict,Any,Text
class Node:
	__slots__='tag','value','start_mark','end_mark','comment','anchor'
	def __init__(A,tag,value,start_mark,end_mark,comment=_A,anchor=_A):A.tag=tag;A.value=value;A.start_mark=start_mark;A.end_mark=end_mark;A.comment=comment;A.anchor=anchor
	def __repr__(A):B=A.value;B=repr(B);return'%s(tag=%r, value=%s)'%(A.__class__.__name__,A.tag,B)
	def dump(A,indent=0):
		E='    {}comment: {})\n';D='  ';B=indent
		if isinstance(A.value,string_types):
			sys.stdout.write('{}{}(tag={!r}, value={!r})\n'.format(D*B,A.__class__.__name__,A.tag,A.value))
			if A.comment:sys.stdout.write(E.format(D*B,A.comment))
			return
		sys.stdout.write('{}{}(tag={!r})\n'.format(D*B,A.__class__.__name__,A.tag))
		if A.comment:sys.stdout.write(E.format(D*B,A.comment))
		for C in A.value:
			if isinstance(C,tuple):
				for F in C:F.dump(B+1)
			elif isinstance(C,Node):C.dump(B+1)
			else:sys.stdout.write('Node value type? {}\n'.format(type(C)))
class ScalarNode(Node):
	__slots__='style',;id='scalar'
	def __init__(A,tag,value,start_mark=_A,end_mark=_A,style=_A,comment=_A,anchor=_A):Node.__init__(A,tag,value,start_mark,end_mark,comment=comment,anchor=anchor);A.style=style
class CollectionNode(Node):
	__slots__='flow_style',
	def __init__(A,tag,value,start_mark=_A,end_mark=_A,flow_style=_A,comment=_A,anchor=_A):Node.__init__(A,tag,value,start_mark,end_mark,comment=comment);A.flow_style=flow_style;A.anchor=anchor
class SequenceNode(CollectionNode):__slots__=();id='sequence'
class MappingNode(CollectionNode):
	__slots__='merge',;id='mapping'
	def __init__(A,tag,value,start_mark=_A,end_mark=_A,flow_style=_A,comment=_A,anchor=_A):CollectionNode.__init__(A,tag,value,start_mark,end_mark,flow_style,comment,anchor);A.merge=_A
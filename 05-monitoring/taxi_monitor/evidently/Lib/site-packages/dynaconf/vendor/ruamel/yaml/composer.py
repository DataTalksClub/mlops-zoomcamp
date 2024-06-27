from __future__ import absolute_import,print_function
_A=None
import warnings
from.error import MarkedYAMLError,ReusedAnchorWarning
from.compat import utf8,nprint,nprintf
from.events import StreamStartEvent,StreamEndEvent,MappingStartEvent,MappingEndEvent,SequenceStartEvent,SequenceEndEvent,AliasEvent,ScalarEvent
from.nodes import MappingNode,ScalarNode,SequenceNode
if False:from typing import Any,Dict,Optional,List
__all__=['Composer','ComposerError']
class ComposerError(MarkedYAMLError):0
class Composer:
	def __init__(A,loader=_A):
		A.loader=loader
		if A.loader is not _A and getattr(A.loader,'_composer',_A)is _A:A.loader._composer=A
		A.anchors={}
	@property
	def parser(self):
		A=self
		if hasattr(A.loader,'typ'):A.loader.parser
		return A.loader._parser
	@property
	def resolver(self):
		A=self
		if hasattr(A.loader,'typ'):A.loader.resolver
		return A.loader._resolver
	def check_node(A):
		if A.parser.check_event(StreamStartEvent):A.parser.get_event()
		return not A.parser.check_event(StreamEndEvent)
	def get_node(A):
		if not A.parser.check_event(StreamEndEvent):return A.compose_document()
	def get_single_node(A):
		A.parser.get_event();B=_A
		if not A.parser.check_event(StreamEndEvent):B=A.compose_document()
		if not A.parser.check_event(StreamEndEvent):C=A.parser.get_event();raise ComposerError('expected a single document in the stream',B.start_mark,'but found another document',C.start_mark)
		A.parser.get_event();return B
	def compose_document(A):A.parser.get_event();B=A.compose_node(_A,_A);A.parser.get_event();A.anchors={};return B
	def compose_node(A,parent,index):
		if A.parser.check_event(AliasEvent):
			C=A.parser.get_event();D=C.anchor
			if D not in A.anchors:raise ComposerError(_A,_A,'found undefined alias %r'%utf8(D),C.start_mark)
			return A.anchors[D]
		C=A.parser.peek_event();B=C.anchor
		if B is not _A:
			if B in A.anchors:F='\nfound duplicate anchor {!r}\nfirst occurrence {}\nsecond occurrence {}'.format(B,A.anchors[B].start_mark,C.start_mark);warnings.warn(F,ReusedAnchorWarning)
		A.resolver.descend_resolver(parent,index)
		if A.parser.check_event(ScalarEvent):E=A.compose_scalar_node(B)
		elif A.parser.check_event(SequenceStartEvent):E=A.compose_sequence_node(B)
		elif A.parser.check_event(MappingStartEvent):E=A.compose_mapping_node(B)
		A.resolver.ascend_resolver();return E
	def compose_scalar_node(C,anchor):
		D=anchor;A=C.parser.get_event();B=A.tag
		if B is _A or B=='!':B=C.resolver.resolve(ScalarNode,A.value,A.implicit)
		E=ScalarNode(B,A.value,A.start_mark,A.end_mark,style=A.style,comment=A.comment,anchor=D)
		if D is not _A:C.anchors[D]=E
		return E
	def compose_sequence_node(B,anchor):
		F=anchor;C=B.parser.get_event();D=C.tag
		if D is _A or D=='!':D=B.resolver.resolve(SequenceNode,_A,C.implicit)
		A=SequenceNode(D,[],C.start_mark,_A,flow_style=C.flow_style,comment=C.comment,anchor=F)
		if F is not _A:B.anchors[F]=A
		G=0
		while not B.parser.check_event(SequenceEndEvent):A.value.append(B.compose_node(A,G));G+=1
		E=B.parser.get_event()
		if A.flow_style is True and E.comment is not _A:
			if A.comment is not _A:nprint('Warning: unexpected end_event commment in sequence node {}'.format(A.flow_style))
			A.comment=E.comment
		A.end_mark=E.end_mark;B.check_end_doc_comment(E,A);return A
	def compose_mapping_node(B,anchor):
		F=anchor;C=B.parser.get_event();D=C.tag
		if D is _A or D=='!':D=B.resolver.resolve(MappingNode,_A,C.implicit)
		A=MappingNode(D,[],C.start_mark,_A,flow_style=C.flow_style,comment=C.comment,anchor=F)
		if F is not _A:B.anchors[F]=A
		while not B.parser.check_event(MappingEndEvent):G=B.compose_node(A,_A);H=B.compose_node(A,G);A.value.append((G,H))
		E=B.parser.get_event()
		if A.flow_style is True and E.comment is not _A:A.comment=E.comment
		A.end_mark=E.end_mark;B.check_end_doc_comment(E,A);return A
	def check_end_doc_comment(C,end_event,node):
		B=node;A=end_event
		if A.comment and A.comment[1]:
			if B.comment is _A:B.comment=[_A,_A]
			assert not isinstance(B,ScalarEvent);B.comment.append(A.comment[1]);A.comment[1]=_A
from __future__ import absolute_import
_E='serializer is not opened'
_D='serializer is closed'
_C=False
_B=True
_A=None
from.error import YAMLError
from.compat import nprint,DBG_NODE,dbg,string_types,nprintf
from.util import RegExp
from.events import StreamStartEvent,StreamEndEvent,MappingStartEvent,MappingEndEvent,SequenceStartEvent,SequenceEndEvent,AliasEvent,ScalarEvent,DocumentStartEvent,DocumentEndEvent
from.nodes import MappingNode,ScalarNode,SequenceNode
if _C:from typing import Any,Dict,Union,Text,Optional;from.compat import VersionType
__all__=['Serializer','SerializerError']
class SerializerError(YAMLError):0
class Serializer:
	ANCHOR_TEMPLATE='id%03d';ANCHOR_RE=RegExp('id(?!000$)\\d{3,}')
	def __init__(A,encoding=_A,explicit_start=_A,explicit_end=_A,version=_A,tags=_A,dumper=_A):
		B=version;A.dumper=dumper
		if A.dumper is not _A:A.dumper._serializer=A
		A.use_encoding=encoding;A.use_explicit_start=explicit_start;A.use_explicit_end=explicit_end
		if isinstance(B,string_types):A.use_version=tuple(map(int,B.split('.')))
		else:A.use_version=B
		A.use_tags=tags;A.serialized_nodes={};A.anchors={};A.last_anchor_id=0;A.closed=_A;A._templated_id=_A
	@property
	def emitter(self):
		A=self
		if hasattr(A.dumper,'typ'):return A.dumper.emitter
		return A.dumper._emitter
	@property
	def resolver(self):
		A=self
		if hasattr(A.dumper,'typ'):A.dumper.resolver
		return A.dumper._resolver
	def open(A):
		if A.closed is _A:A.emitter.emit(StreamStartEvent(encoding=A.use_encoding));A.closed=_C
		elif A.closed:raise SerializerError(_D)
		else:raise SerializerError('serializer is already opened')
	def close(A):
		if A.closed is _A:raise SerializerError(_E)
		elif not A.closed:A.emitter.emit(StreamEndEvent());A.closed=_B
	def serialize(A,node):
		B=node
		if dbg(DBG_NODE):nprint('Serializing nodes');B.dump()
		if A.closed is _A:raise SerializerError(_E)
		elif A.closed:raise SerializerError(_D)
		A.emitter.emit(DocumentStartEvent(explicit=A.use_explicit_start,version=A.use_version,tags=A.use_tags));A.anchor_node(B);A.serialize_node(B,_A,_A);A.emitter.emit(DocumentEndEvent(explicit=A.use_explicit_end));A.serialized_nodes={};A.anchors={};A.last_anchor_id=0
	def anchor_node(B,node):
		A=node
		if A in B.anchors:
			if B.anchors[A]is _A:B.anchors[A]=B.generate_anchor(A)
		else:
			C=_A
			try:
				if A.anchor.always_dump:C=A.anchor.value
			except:pass
			B.anchors[A]=C
			if isinstance(A,SequenceNode):
				for D in A.value:B.anchor_node(D)
			elif isinstance(A,MappingNode):
				for(E,F)in A.value:B.anchor_node(E);B.anchor_node(F)
	def generate_anchor(A,node):
		try:B=node.anchor.value
		except:B=_A
		if B is _A:A.last_anchor_id+=1;return A.ANCHOR_TEMPLATE%A.last_anchor_id
		return B
	def serialize_node(B,node,parent,index):
		F=index;A=node;G=B.anchors[A]
		if A in B.serialized_nodes:B.emitter.emit(AliasEvent(G))
		else:
			B.serialized_nodes[A]=_B;B.resolver.descend_resolver(parent,F)
			if isinstance(A,ScalarNode):K=B.resolver.resolve(ScalarNode,A.value,(_B,_C));L=B.resolver.resolve(ScalarNode,A.value,(_C,_B));E=A.tag==K,A.tag==L,A.tag.startswith('tag:yaml.org,2002:');B.emitter.emit(ScalarEvent(G,A.tag,E,A.value,style=A.style,comment=A.comment))
			elif isinstance(A,SequenceNode):
				E=A.tag==B.resolver.resolve(SequenceNode,A.value,_B);C=A.comment;D=_A;H=_A
				if A.flow_style is _B:
					if C:H=C[0]
				if C and len(C)>2:D=C[2]
				else:D=_A
				B.emitter.emit(SequenceStartEvent(G,A.tag,E,flow_style=A.flow_style,comment=A.comment));F=0
				for M in A.value:B.serialize_node(M,A,F);F+=1
				B.emitter.emit(SequenceEndEvent(comment=[H,D]))
			elif isinstance(A,MappingNode):
				E=A.tag==B.resolver.resolve(MappingNode,A.value,_B);C=A.comment;D=_A;I=_A
				if A.flow_style is _B:
					if C:I=C[0]
				if C and len(C)>2:D=C[2]
				B.emitter.emit(MappingStartEvent(G,A.tag,E,flow_style=A.flow_style,comment=A.comment,nr_items=len(A.value)))
				for(J,N)in A.value:B.serialize_node(J,A,_A);B.serialize_node(N,A,J)
				B.emitter.emit(MappingEndEvent(comment=[I,D]))
			B.resolver.ascend_resolver()
def templated_id(s):return Serializer.ANCHOR_RE.match(s)
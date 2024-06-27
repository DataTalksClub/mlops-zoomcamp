from __future__ import absolute_import,print_function
_T='\ufeff'
_S='\ue000'
_R='\ud7ff'
_Q='%%%02X'
_P='version'
_O="-;/?:@&=+$,_.~*'()[]"
_N=' \n\x85\u2028\u2029'
_M='\xa0'
_L='...'
_K='\\'
_J="'"
_I='?'
_H='"'
_G='!'
_F='\n\x85\u2028\u2029'
_E='\n'
_D=' '
_C=False
_B=None
_A=True
import sys
from.error import YAMLError,YAMLStreamError
from.events import*
from.compat import utf8,text_type,PY2,nprint,dbg,DBG_EVENT,check_anchorname_char
if _C:from typing import Any,Dict,List,Union,Text,Tuple,Optional;from.compat import StreamType
__all__=['Emitter','EmitterError']
class EmitterError(YAMLError):0
class ScalarAnalysis:
	def __init__(self,scalar,empty,multiline,allow_flow_plain,allow_block_plain,allow_single_quoted,allow_double_quoted,allow_block):self.scalar=scalar;self.empty=empty;self.multiline=multiline;self.allow_flow_plain=allow_flow_plain;self.allow_block_plain=allow_block_plain;self.allow_single_quoted=allow_single_quoted;self.allow_double_quoted=allow_double_quoted;self.allow_block=allow_block
class Indents:
	def __init__(self):self.values=[]
	def append(self,val,seq):self.values.append((val,seq))
	def pop(self):return self.values.pop()[0]
	def last_seq(self):
		try:return self.values[-2][1]
		except IndexError:return _C
	def seq_flow_align(self,seq_indent,column):
		if len(self.values)<2 or not self.values[-1][1]:return 0
		base=self.values[-1][0]if self.values[-1][0]is not _B else 0;return base+seq_indent-column-1
	def __len__(self):return len(self.values)
class Emitter:
	DEFAULT_TAG_PREFIXES={_G:_G,'tag:yaml.org,2002:':'!!'};MAX_SIMPLE_KEY_LENGTH=128
	def __init__(self,stream,canonical=_B,indent=_B,width=_B,allow_unicode=_B,line_break=_B,block_seq_indent=_B,top_level_colon_align=_B,prefix_colon=_B,brace_single_entry_mapping_in_flow_sequence=_B,dumper=_B):
		self.dumper=dumper
		if self.dumper is not _B and getattr(self.dumper,'_emitter',_B)is _B:self.dumper._emitter=self
		self.stream=stream;self.encoding=_B;self.allow_space_break=_B;self.states=[];self.state=self.expect_stream_start;self.events=[];self.event=_B;self.indents=Indents();self.indent=_B;self.flow_context=[];self.root_context=_C;self.sequence_context=_C;self.mapping_context=_C;self.simple_key_context=_C;self.line=0;self.column=0;self.whitespace=_A;self.indention=_A;self.compact_seq_seq=_A;self.compact_seq_map=_A;self.no_newline=_B;self.open_ended=_C;self.colon=':';self.prefixed_colon=self.colon if prefix_colon is _B else prefix_colon+self.colon;self.brace_single_entry_mapping_in_flow_sequence=brace_single_entry_mapping_in_flow_sequence;self.canonical=canonical;self.allow_unicode=allow_unicode;self.unicode_supplementary=sys.maxunicode>65535;self.sequence_dash_offset=block_seq_indent if block_seq_indent else 0;self.top_level_colon_align=top_level_colon_align;self.best_sequence_indent=2;self.requested_indent=indent
		if indent and 1<indent<10:self.best_sequence_indent=indent
		self.best_map_indent=self.best_sequence_indent;self.best_width=80
		if width and width>self.best_sequence_indent*2:self.best_width=width
		self.best_line_break=_E
		if line_break in['\r',_E,'\r\n']:self.best_line_break=line_break
		self.tag_prefixes=_B;self.prepared_anchor=_B;self.prepared_tag=_B;self.analysis=_B;self.style=_B;self.scalar_after_indicator=_A
	@property
	def stream(self):
		try:return self._stream
		except AttributeError:raise YAMLStreamError('output stream needs to specified')
	@stream.setter
	def stream(self,val):
		if val is _B:return
		if not hasattr(val,'write'):raise YAMLStreamError('stream argument needs to have a write() method')
		self._stream=val
	@property
	def serializer(self):
		try:
			if hasattr(self.dumper,'typ'):return self.dumper.serializer
			return self.dumper._serializer
		except AttributeError:return self
	@property
	def flow_level(self):return len(self.flow_context)
	def dispose(self):self.states=[];self.state=_B
	def emit(self,event):
		if dbg(DBG_EVENT):nprint(event)
		self.events.append(event)
		while not self.need_more_events():self.event=self.events.pop(0);self.state();self.event=_B
	def need_more_events(self):
		if not self.events:return _A
		event=self.events[0]
		if isinstance(event,DocumentStartEvent):return self.need_events(1)
		elif isinstance(event,SequenceStartEvent):return self.need_events(2)
		elif isinstance(event,MappingStartEvent):return self.need_events(3)
		else:return _C
	def need_events(self,count):
		level=0
		for event in self.events[1:]:
			if isinstance(event,(DocumentStartEvent,CollectionStartEvent)):level+=1
			elif isinstance(event,(DocumentEndEvent,CollectionEndEvent)):level-=1
			elif isinstance(event,StreamEndEvent):level=-1
			if level<0:return _C
		return len(self.events)<count+1
	def increase_indent(self,flow=_C,sequence=_B,indentless=_C):
		self.indents.append(self.indent,sequence)
		if self.indent is _B:
			if flow:self.indent=self.requested_indent
			else:self.indent=0
		elif not indentless:self.indent+=self.best_sequence_indent if self.indents.last_seq()else self.best_map_indent
	def expect_stream_start(self):
		A='encoding'
		if isinstance(self.event,StreamStartEvent):
			if PY2:
				if self.event.encoding and not getattr(self.stream,A,_B):self.encoding=self.event.encoding
			elif self.event.encoding and not hasattr(self.stream,A):self.encoding=self.event.encoding
			self.write_stream_start();self.state=self.expect_first_document_start
		else:raise EmitterError('expected StreamStartEvent, but got %s'%(self.event,))
	def expect_nothing(self):raise EmitterError('expected nothing, but got %s'%(self.event,))
	def expect_first_document_start(self):return self.expect_document_start(first=_A)
	def expect_document_start(self,first=_C):
		if isinstance(self.event,DocumentStartEvent):
			if(self.event.version or self.event.tags)and self.open_ended:self.write_indicator(_L,_A);self.write_indent()
			if self.event.version:version_text=self.prepare_version(self.event.version);self.write_version_directive(version_text)
			self.tag_prefixes=self.DEFAULT_TAG_PREFIXES.copy()
			if self.event.tags:
				handles=sorted(self.event.tags.keys())
				for handle in handles:prefix=self.event.tags[handle];self.tag_prefixes[prefix]=handle;handle_text=self.prepare_tag_handle(handle);prefix_text=self.prepare_tag_prefix(prefix);self.write_tag_directive(handle_text,prefix_text)
			implicit=first and not self.event.explicit and not self.canonical and not self.event.version and not self.event.tags and not self.check_empty_document()
			if not implicit:
				self.write_indent();self.write_indicator('---',_A)
				if self.canonical:self.write_indent()
			self.state=self.expect_document_root
		elif isinstance(self.event,StreamEndEvent):
			if self.open_ended:self.write_indicator(_L,_A);self.write_indent()
			self.write_stream_end();self.state=self.expect_nothing
		else:raise EmitterError('expected DocumentStartEvent, but got %s'%(self.event,))
	def expect_document_end(self):
		if isinstance(self.event,DocumentEndEvent):
			self.write_indent()
			if self.event.explicit:self.write_indicator(_L,_A);self.write_indent()
			self.flush_stream();self.state=self.expect_document_start
		else:raise EmitterError('expected DocumentEndEvent, but got %s'%(self.event,))
	def expect_document_root(self):self.states.append(self.expect_document_end);self.expect_node(root=_A)
	def expect_node(self,root=_C,sequence=_C,mapping=_C,simple_key=_C):
		self.root_context=root;self.sequence_context=sequence;self.mapping_context=mapping;self.simple_key_context=simple_key
		if isinstance(self.event,AliasEvent):self.expect_alias()
		elif isinstance(self.event,(ScalarEvent,CollectionStartEvent)):
			if self.process_anchor('&')and isinstance(self.event,ScalarEvent)and self.sequence_context:self.sequence_context=_C
			if root and isinstance(self.event,ScalarEvent)and not self.scalar_after_indicator:self.write_indent()
			self.process_tag()
			if isinstance(self.event,ScalarEvent):self.expect_scalar()
			elif isinstance(self.event,SequenceStartEvent):
				i2,n2=self.indention,self.no_newline
				if self.event.comment:
					if self.event.flow_style is _C and self.event.comment:
						if self.write_post_comment(self.event):self.indention=_C;self.no_newline=_A
					if self.write_pre_comment(self.event):self.indention=i2;self.no_newline=not self.indention
				if self.flow_level or self.canonical or self.event.flow_style or self.check_empty_sequence():self.expect_flow_sequence()
				else:self.expect_block_sequence()
			elif isinstance(self.event,MappingStartEvent):
				if self.event.flow_style is _C and self.event.comment:self.write_post_comment(self.event)
				if self.event.comment and self.event.comment[1]:self.write_pre_comment(self.event)
				if self.flow_level or self.canonical or self.event.flow_style or self.check_empty_mapping():self.expect_flow_mapping(single=self.event.nr_items==1)
				else:self.expect_block_mapping()
		else:raise EmitterError('expected NodeEvent, but got %s'%(self.event,))
	def expect_alias(self):
		if self.event.anchor is _B:raise EmitterError('anchor is not specified for alias')
		self.process_anchor('*');self.state=self.states.pop()
	def expect_scalar(self):self.increase_indent(flow=_A);self.process_scalar();self.indent=self.indents.pop();self.state=self.states.pop()
	def expect_flow_sequence(self):ind=self.indents.seq_flow_align(self.best_sequence_indent,self.column);self.write_indicator(_D*ind+'[',_A,whitespace=_A);self.increase_indent(flow=_A,sequence=_A);self.flow_context.append('[');self.state=self.expect_first_flow_sequence_item
	def expect_first_flow_sequence_item(self):
		if isinstance(self.event,SequenceEndEvent):
			self.indent=self.indents.pop();popped=self.flow_context.pop();assert popped=='[';self.write_indicator(']',_C)
			if self.event.comment and self.event.comment[0]:self.write_post_comment(self.event)
			elif self.flow_level==0:self.write_line_break()
			self.state=self.states.pop()
		else:
			if self.canonical or self.column>self.best_width:self.write_indent()
			self.states.append(self.expect_flow_sequence_item);self.expect_node(sequence=_A)
	def expect_flow_sequence_item(self):
		if isinstance(self.event,SequenceEndEvent):
			self.indent=self.indents.pop();popped=self.flow_context.pop();assert popped=='['
			if self.canonical:self.write_indicator(',',_C);self.write_indent()
			self.write_indicator(']',_C)
			if self.event.comment and self.event.comment[0]:self.write_post_comment(self.event)
			else:self.no_newline=_C
			self.state=self.states.pop()
		else:
			self.write_indicator(',',_C)
			if self.canonical or self.column>self.best_width:self.write_indent()
			self.states.append(self.expect_flow_sequence_item);self.expect_node(sequence=_A)
	def expect_flow_mapping(self,single=_C):
		ind=self.indents.seq_flow_align(self.best_sequence_indent,self.column);map_init='{'
		if single and self.flow_level and self.flow_context[-1]=='['and not self.canonical and not self.brace_single_entry_mapping_in_flow_sequence:map_init=''
		self.write_indicator(_D*ind+map_init,_A,whitespace=_A);self.flow_context.append(map_init);self.increase_indent(flow=_A,sequence=_C);self.state=self.expect_first_flow_mapping_key
	def expect_first_flow_mapping_key(self):
		if isinstance(self.event,MappingEndEvent):
			self.indent=self.indents.pop();popped=self.flow_context.pop();assert popped=='{';self.write_indicator('}',_C)
			if self.event.comment and self.event.comment[0]:self.write_post_comment(self.event)
			elif self.flow_level==0:self.write_line_break()
			self.state=self.states.pop()
		else:
			if self.canonical or self.column>self.best_width:self.write_indent()
			if not self.canonical and self.check_simple_key():self.states.append(self.expect_flow_mapping_simple_value);self.expect_node(mapping=_A,simple_key=_A)
			else:self.write_indicator(_I,_A);self.states.append(self.expect_flow_mapping_value);self.expect_node(mapping=_A)
	def expect_flow_mapping_key(self):
		if isinstance(self.event,MappingEndEvent):
			self.indent=self.indents.pop();popped=self.flow_context.pop();assert popped in['{','']
			if self.canonical:self.write_indicator(',',_C);self.write_indent()
			if popped!='':self.write_indicator('}',_C)
			if self.event.comment and self.event.comment[0]:self.write_post_comment(self.event)
			else:self.no_newline=_C
			self.state=self.states.pop()
		else:
			self.write_indicator(',',_C)
			if self.canonical or self.column>self.best_width:self.write_indent()
			if not self.canonical and self.check_simple_key():self.states.append(self.expect_flow_mapping_simple_value);self.expect_node(mapping=_A,simple_key=_A)
			else:self.write_indicator(_I,_A);self.states.append(self.expect_flow_mapping_value);self.expect_node(mapping=_A)
	def expect_flow_mapping_simple_value(self):self.write_indicator(self.prefixed_colon,_C);self.states.append(self.expect_flow_mapping_key);self.expect_node(mapping=_A)
	def expect_flow_mapping_value(self):
		if self.canonical or self.column>self.best_width:self.write_indent()
		self.write_indicator(self.prefixed_colon,_A);self.states.append(self.expect_flow_mapping_key);self.expect_node(mapping=_A)
	def expect_block_sequence(self):
		if self.mapping_context:indentless=not self.indention
		else:
			indentless=_C
			if not self.compact_seq_seq and self.column!=0:self.write_line_break()
		self.increase_indent(flow=_C,sequence=_A,indentless=indentless);self.state=self.expect_first_block_sequence_item
	def expect_first_block_sequence_item(self):return self.expect_block_sequence_item(first=_A)
	def expect_block_sequence_item(self,first=_C):
		if not first and isinstance(self.event,SequenceEndEvent):
			if self.event.comment and self.event.comment[1]:self.write_pre_comment(self.event)
			self.indent=self.indents.pop();self.state=self.states.pop();self.no_newline=_C
		else:
			if self.event.comment and self.event.comment[1]:self.write_pre_comment(self.event)
			nonl=self.no_newline if self.column==0 else _C;self.write_indent();ind=self.sequence_dash_offset;self.write_indicator(_D*ind+'-',_A,indention=_A)
			if nonl or self.sequence_dash_offset+2>self.best_sequence_indent:self.no_newline=_A
			self.states.append(self.expect_block_sequence_item);self.expect_node(sequence=_A)
	def expect_block_mapping(self):
		if not self.mapping_context and not(self.compact_seq_map or self.column==0):self.write_line_break()
		self.increase_indent(flow=_C,sequence=_C);self.state=self.expect_first_block_mapping_key
	def expect_first_block_mapping_key(self):return self.expect_block_mapping_key(first=_A)
	def expect_block_mapping_key(self,first=_C):
		if not first and isinstance(self.event,MappingEndEvent):
			if self.event.comment and self.event.comment[1]:self.write_pre_comment(self.event)
			self.indent=self.indents.pop();self.state=self.states.pop()
		else:
			if self.event.comment and self.event.comment[1]:self.write_pre_comment(self.event)
			self.write_indent()
			if self.check_simple_key():
				if not isinstance(self.event,(SequenceStartEvent,MappingStartEvent)):
					try:
						if self.event.style==_I:self.write_indicator(_I,_A,indention=_A)
					except AttributeError:pass
				self.states.append(self.expect_block_mapping_simple_value);self.expect_node(mapping=_A,simple_key=_A)
				if isinstance(self.event,AliasEvent):self.stream.write(_D)
			else:self.write_indicator(_I,_A,indention=_A);self.states.append(self.expect_block_mapping_value);self.expect_node(mapping=_A)
	def expect_block_mapping_simple_value(self):
		if getattr(self.event,'style',_B)!=_I:
			if self.indent==0 and self.top_level_colon_align is not _B:c=_D*(self.top_level_colon_align-self.column)+self.colon
			else:c=self.prefixed_colon
			self.write_indicator(c,_C)
		self.states.append(self.expect_block_mapping_key);self.expect_node(mapping=_A)
	def expect_block_mapping_value(self):self.write_indent();self.write_indicator(self.prefixed_colon,_A,indention=_A);self.states.append(self.expect_block_mapping_key);self.expect_node(mapping=_A)
	def check_empty_sequence(self):return isinstance(self.event,SequenceStartEvent)and bool(self.events)and isinstance(self.events[0],SequenceEndEvent)
	def check_empty_mapping(self):return isinstance(self.event,MappingStartEvent)and bool(self.events)and isinstance(self.events[0],MappingEndEvent)
	def check_empty_document(self):
		if not isinstance(self.event,DocumentStartEvent)or not self.events:return _C
		event=self.events[0];return isinstance(event,ScalarEvent)and event.anchor is _B and event.tag is _B and event.implicit and event.value==''
	def check_simple_key(self):
		length=0
		if isinstance(self.event,NodeEvent)and self.event.anchor is not _B:
			if self.prepared_anchor is _B:self.prepared_anchor=self.prepare_anchor(self.event.anchor)
			length+=len(self.prepared_anchor)
		if isinstance(self.event,(ScalarEvent,CollectionStartEvent))and self.event.tag is not _B:
			if self.prepared_tag is _B:self.prepared_tag=self.prepare_tag(self.event.tag)
			length+=len(self.prepared_tag)
		if isinstance(self.event,ScalarEvent):
			if self.analysis is _B:self.analysis=self.analyze_scalar(self.event.value)
			length+=len(self.analysis.scalar)
		return length<self.MAX_SIMPLE_KEY_LENGTH and(isinstance(self.event,AliasEvent)or isinstance(self.event,SequenceStartEvent)and self.event.flow_style is _A or isinstance(self.event,MappingStartEvent)and self.event.flow_style is _A or isinstance(self.event,ScalarEvent)and not(self.analysis.empty and self.style and self.style not in'\'"')and not self.analysis.multiline or self.check_empty_sequence()or self.check_empty_mapping())
	def process_anchor(self,indicator):
		if self.event.anchor is _B:self.prepared_anchor=_B;return _C
		if self.prepared_anchor is _B:self.prepared_anchor=self.prepare_anchor(self.event.anchor)
		if self.prepared_anchor:self.write_indicator(indicator+self.prepared_anchor,_A);self.no_newline=_C
		self.prepared_anchor=_B;return _A
	def process_tag(self):
		tag=self.event.tag
		if isinstance(self.event,ScalarEvent):
			if self.style is _B:self.style=self.choose_scalar_style()
			if(not self.canonical or tag is _B)and(self.style==''and self.event.implicit[0]or self.style!=''and self.event.implicit[1]):self.prepared_tag=_B;return
			if self.event.implicit[0]and tag is _B:tag=_G;self.prepared_tag=_B
		elif(not self.canonical or tag is _B)and self.event.implicit:self.prepared_tag=_B;return
		if tag is _B:raise EmitterError('tag is not specified')
		if self.prepared_tag is _B:self.prepared_tag=self.prepare_tag(tag)
		if self.prepared_tag:
			self.write_indicator(self.prepared_tag,_A)
			if self.sequence_context and not self.flow_level and isinstance(self.event,ScalarEvent):self.no_newline=_A
		self.prepared_tag=_B
	def choose_scalar_style(self):
		if self.analysis is _B:self.analysis=self.analyze_scalar(self.event.value)
		if self.event.style==_H or self.canonical:return _H
		if(not self.event.style or self.event.style==_I)and(self.event.implicit[0]or not self.event.implicit[2]):
			if not(self.simple_key_context and(self.analysis.empty or self.analysis.multiline))and(self.flow_level and self.analysis.allow_flow_plain or not self.flow_level and self.analysis.allow_block_plain):return''
		self.analysis.allow_block=_A
		if self.event.style and self.event.style in'|>':
			if not self.flow_level and not self.simple_key_context and self.analysis.allow_block:return self.event.style
		if not self.event.style and self.analysis.allow_double_quoted:
			if _J in self.event.value or _E in self.event.value:return _H
		if not self.event.style or self.event.style==_J:
			if self.analysis.allow_single_quoted and not(self.simple_key_context and self.analysis.multiline):return _J
		return _H
	def process_scalar(self):
		if self.analysis is _B:self.analysis=self.analyze_scalar(self.event.value)
		if self.style is _B:self.style=self.choose_scalar_style()
		split=not self.simple_key_context
		if self.sequence_context and not self.flow_level:self.write_indent()
		if self.style==_H:self.write_double_quoted(self.analysis.scalar,split)
		elif self.style==_J:self.write_single_quoted(self.analysis.scalar,split)
		elif self.style=='>':self.write_folded(self.analysis.scalar)
		elif self.style=='|':self.write_literal(self.analysis.scalar,self.event.comment)
		else:self.write_plain(self.analysis.scalar,split)
		self.analysis=_B;self.style=_B
		if self.event.comment:self.write_post_comment(self.event)
	def prepare_version(self,version):
		major,minor=version
		if major!=1:raise EmitterError('unsupported YAML version: %d.%d'%(major,minor))
		return'%d.%d'%(major,minor)
	def prepare_tag_handle(self,handle):
		if not handle:raise EmitterError('tag handle must not be empty')
		if handle[0]!=_G or handle[-1]!=_G:raise EmitterError("tag handle must start and end with '!': %r"%utf8(handle))
		for ch in handle[1:-1]:
			if not('0'<=ch<='9'or'A'<=ch<='Z'or'a'<=ch<='z'or ch in'-_'):raise EmitterError('invalid character %r in the tag handle: %r'%(utf8(ch),utf8(handle)))
		return handle
	def prepare_tag_prefix(self,prefix):
		if not prefix:raise EmitterError('tag prefix must not be empty')
		chunks=[];start=end=0
		if prefix[0]==_G:end=1
		ch_set=_O
		if self.dumper:
			version=getattr(self.dumper,_P,(1,2))
			if version is _B or version>=(1,2):ch_set+='#'
		while end<len(prefix):
			ch=prefix[end]
			if'0'<=ch<='9'or'A'<=ch<='Z'or'a'<=ch<='z'or ch in ch_set:end+=1
			else:
				if start<end:chunks.append(prefix[start:end])
				start=end=end+1;data=utf8(ch)
				for ch in data:chunks.append(_Q%ord(ch))
		if start<end:chunks.append(prefix[start:end])
		return''.join(chunks)
	def prepare_tag(self,tag):
		if not tag:raise EmitterError('tag must not be empty')
		if tag==_G:return tag
		handle=_B;suffix=tag;prefixes=sorted(self.tag_prefixes.keys())
		for prefix in prefixes:
			if tag.startswith(prefix)and(prefix==_G or len(prefix)<len(tag)):handle=self.tag_prefixes[prefix];suffix=tag[len(prefix):]
		chunks=[];start=end=0;ch_set=_O
		if self.dumper:
			version=getattr(self.dumper,_P,(1,2))
			if version is _B or version>=(1,2):ch_set+='#'
		while end<len(suffix):
			ch=suffix[end]
			if'0'<=ch<='9'or'A'<=ch<='Z'or'a'<=ch<='z'or ch in ch_set or ch==_G and handle!=_G:end+=1
			else:
				if start<end:chunks.append(suffix[start:end])
				start=end=end+1;data=utf8(ch)
				for ch in data:chunks.append(_Q%ord(ch))
		if start<end:chunks.append(suffix[start:end])
		suffix_text=''.join(chunks)
		if handle:return'%s%s'%(handle,suffix_text)
		else:return'!<%s>'%suffix_text
	def prepare_anchor(self,anchor):
		if not anchor:raise EmitterError('anchor must not be empty')
		for ch in anchor:
			if not check_anchorname_char(ch):raise EmitterError('invalid character %r in the anchor: %r'%(utf8(ch),utf8(anchor)))
		return anchor
	def analyze_scalar(self,scalar):
		A='\x00 \t\r\n\x85\u2028\u2029'
		if not scalar:return ScalarAnalysis(scalar=scalar,empty=_A,multiline=_C,allow_flow_plain=_C,allow_block_plain=_A,allow_single_quoted=_A,allow_double_quoted=_A,allow_block=_C)
		block_indicators=_C;flow_indicators=_C;line_breaks=_C;special_characters=_C;leading_space=_C;leading_break=_C;trailing_space=_C;trailing_break=_C;break_space=_C;space_break=_C
		if scalar.startswith('---')or scalar.startswith(_L):block_indicators=_A;flow_indicators=_A
		preceeded_by_whitespace=_A;followed_by_whitespace=len(scalar)==1 or scalar[1]in A;previous_space=_C;previous_break=_C;index=0
		while index<len(scalar):
			ch=scalar[index]
			if index==0:
				if ch in'#,[]{}&*!|>\'"%@`':flow_indicators=_A;block_indicators=_A
				if ch in'?:':
					if self.serializer.use_version==(1,1):flow_indicators=_A
					elif len(scalar)==1:flow_indicators=_A
					if followed_by_whitespace:block_indicators=_A
				if ch=='-'and followed_by_whitespace:flow_indicators=_A;block_indicators=_A
			else:
				if ch in',[]{}':flow_indicators=_A
				if ch==_I and self.serializer.use_version==(1,1):flow_indicators=_A
				if ch==':':
					if followed_by_whitespace:flow_indicators=_A;block_indicators=_A
				if ch=='#'and preceeded_by_whitespace:flow_indicators=_A;block_indicators=_A
			if ch in _F:line_breaks=_A
			if not(ch==_E or _D<=ch<='~'):
				if(ch=='\x85'or _M<=ch<=_R or _S<=ch<='�'or self.unicode_supplementary and'𐀀'<=ch<='\U0010ffff')and ch!=_T:
					if not self.allow_unicode:special_characters=_A
				else:special_characters=_A
			if ch==_D:
				if index==0:leading_space=_A
				if index==len(scalar)-1:trailing_space=_A
				if previous_break:break_space=_A
				previous_space=_A;previous_break=_C
			elif ch in _F:
				if index==0:leading_break=_A
				if index==len(scalar)-1:trailing_break=_A
				if previous_space:space_break=_A
				previous_space=_C;previous_break=_A
			else:previous_space=_C;previous_break=_C
			index+=1;preceeded_by_whitespace=ch in A;followed_by_whitespace=index+1>=len(scalar)or scalar[index+1]in A
		allow_flow_plain=_A;allow_block_plain=_A;allow_single_quoted=_A;allow_double_quoted=_A;allow_block=_A
		if leading_space or leading_break or trailing_space or trailing_break:allow_flow_plain=allow_block_plain=_C
		if trailing_space:allow_block=_C
		if break_space:allow_flow_plain=allow_block_plain=allow_single_quoted=_C
		if special_characters:allow_flow_plain=allow_block_plain=allow_single_quoted=allow_block=_C
		elif space_break:
			allow_flow_plain=allow_block_plain=allow_single_quoted=_C
			if not self.allow_space_break:allow_block=_C
		if line_breaks:allow_flow_plain=allow_block_plain=_C
		if flow_indicators:allow_flow_plain=_C
		if block_indicators:allow_block_plain=_C
		return ScalarAnalysis(scalar=scalar,empty=_C,multiline=line_breaks,allow_flow_plain=allow_flow_plain,allow_block_plain=allow_block_plain,allow_single_quoted=allow_single_quoted,allow_double_quoted=allow_double_quoted,allow_block=allow_block)
	def flush_stream(self):
		if hasattr(self.stream,'flush'):self.stream.flush()
	def write_stream_start(self):
		if self.encoding and self.encoding.startswith('utf-16'):self.stream.write(_T.encode(self.encoding))
	def write_stream_end(self):self.flush_stream()
	def write_indicator(self,indicator,need_whitespace,whitespace=_C,indention=_C):
		if self.whitespace or not need_whitespace:data=indicator
		else:data=_D+indicator
		self.whitespace=whitespace;self.indention=self.indention and indention;self.column+=len(data);self.open_ended=_C
		if bool(self.encoding):data=data.encode(self.encoding)
		self.stream.write(data)
	def write_indent(self):
		indent=self.indent or 0
		if not self.indention or self.column>indent or self.column==indent and not self.whitespace:
			if bool(self.no_newline):self.no_newline=_C
			else:self.write_line_break()
		if self.column<indent:
			self.whitespace=_A;data=_D*(indent-self.column);self.column=indent
			if self.encoding:data=data.encode(self.encoding)
			self.stream.write(data)
	def write_line_break(self,data=_B):
		if data is _B:data=self.best_line_break
		self.whitespace=_A;self.indention=_A;self.line+=1;self.column=0
		if bool(self.encoding):data=data.encode(self.encoding)
		self.stream.write(data)
	def write_version_directive(self,version_text):
		data='%%YAML %s'%version_text
		if self.encoding:data=data.encode(self.encoding)
		self.stream.write(data);self.write_line_break()
	def write_tag_directive(self,handle_text,prefix_text):
		data='%%TAG %s %s'%(handle_text,prefix_text)
		if self.encoding:data=data.encode(self.encoding)
		self.stream.write(data);self.write_line_break()
	def write_single_quoted(self,text,split=_A):
		if self.root_context:
			if self.requested_indent is not _B:
				self.write_line_break()
				if self.requested_indent!=0:self.write_indent()
		self.write_indicator(_J,_A);spaces=_C;breaks=_C;start=end=0
		while end<=len(text):
			ch=_B
			if end<len(text):ch=text[end]
			if spaces:
				if ch is _B or ch!=_D:
					if start+1==end and self.column>self.best_width and split and start!=0 and end!=len(text):self.write_indent()
					else:
						data=text[start:end];self.column+=len(data)
						if bool(self.encoding):data=data.encode(self.encoding)
						self.stream.write(data)
					start=end
			elif breaks:
				if ch is _B or ch not in _F:
					if text[start]==_E:self.write_line_break()
					for br in text[start:end]:
						if br==_E:self.write_line_break()
						else:self.write_line_break(br)
					self.write_indent();start=end
			elif ch is _B or ch in _N or ch==_J:
				if start<end:
					data=text[start:end];self.column+=len(data)
					if bool(self.encoding):data=data.encode(self.encoding)
					self.stream.write(data);start=end
			if ch==_J:
				data="''";self.column+=2
				if bool(self.encoding):data=data.encode(self.encoding)
				self.stream.write(data);start=end+1
			if ch is not _B:spaces=ch==_D;breaks=ch in _F
			end+=1
		self.write_indicator(_J,_C)
	ESCAPE_REPLACEMENTS={'\x00':'0','\x07':'a','\x08':'b','\t':'t',_E:'n','\x0b':'v','\x0c':'f','\r':'r','\x1b':'e',_H:_H,_K:_K,'\x85':'N',_M:'_','\u2028':'L','\u2029':'P'}
	def write_double_quoted(self,text,split=_A):
		if self.root_context:
			if self.requested_indent is not _B:
				self.write_line_break()
				if self.requested_indent!=0:self.write_indent()
		self.write_indicator(_H,_A);start=end=0
		while end<=len(text):
			ch=_B
			if end<len(text):ch=text[end]
			if ch is _B or ch in'"\\\x85\u2028\u2029\ufeff'or not(_D<=ch<='~'or self.allow_unicode and(_M<=ch<=_R or _S<=ch<='�')):
				if start<end:
					data=text[start:end];self.column+=len(data)
					if bool(self.encoding):data=data.encode(self.encoding)
					self.stream.write(data);start=end
				if ch is not _B:
					if ch in self.ESCAPE_REPLACEMENTS:data=_K+self.ESCAPE_REPLACEMENTS[ch]
					elif ch<='ÿ':data='\\x%02X'%ord(ch)
					elif ch<='\uffff':data='\\u%04X'%ord(ch)
					else:data='\\U%08X'%ord(ch)
					self.column+=len(data)
					if bool(self.encoding):data=data.encode(self.encoding)
					self.stream.write(data);start=end+1
			if 0<end<len(text)-1 and(ch==_D or start>=end)and self.column+(end-start)>self.best_width and split:
				data=text[start:end]+_K
				if start<end:start=end
				self.column+=len(data)
				if bool(self.encoding):data=data.encode(self.encoding)
				self.stream.write(data);self.write_indent();self.whitespace=_C;self.indention=_C
				if text[start]==_D:
					data=_K;self.column+=len(data)
					if bool(self.encoding):data=data.encode(self.encoding)
					self.stream.write(data)
			end+=1
		self.write_indicator(_H,_C)
	def determine_block_hints(self,text):
		indent=0;indicator='';hints=''
		if text:
			if text[0]in _N:indent=self.best_sequence_indent;hints+=text_type(indent)
			elif self.root_context:
				for end in['\n---','\n...']:
					pos=0
					while _A:
						pos=text.find(end,pos)
						if pos==-1:break
						try:
							if text[pos+4]in' \r\n':break
						except IndexError:pass
						pos+=1
					if pos>-1:break
				if pos>0:indent=self.best_sequence_indent
			if text[-1]not in _F:indicator='-'
			elif len(text)==1 or text[-2]in _F:indicator='+'
		hints+=indicator;return hints,indent,indicator
	def write_folded(self,text):
		hints,_indent,_indicator=self.determine_block_hints(text);self.write_indicator('>'+hints,_A)
		if _indicator=='+':self.open_ended=_A
		self.write_line_break();leading_space=_A;spaces=_C;breaks=_A;start=end=0
		while end<=len(text):
			ch=_B
			if end<len(text):ch=text[end]
			if breaks:
				if ch is _B or ch not in'\n\x85\u2028\u2029\x07':
					if not leading_space and ch is not _B and ch!=_D and text[start]==_E:self.write_line_break()
					leading_space=ch==_D
					for br in text[start:end]:
						if br==_E:self.write_line_break()
						else:self.write_line_break(br)
					if ch is not _B:self.write_indent()
					start=end
			elif spaces:
				if ch!=_D:
					if start+1==end and self.column>self.best_width:self.write_indent()
					else:
						data=text[start:end];self.column+=len(data)
						if bool(self.encoding):data=data.encode(self.encoding)
						self.stream.write(data)
					start=end
			elif ch is _B or ch in' \n\x85\u2028\u2029\x07':
				data=text[start:end];self.column+=len(data)
				if bool(self.encoding):data=data.encode(self.encoding)
				self.stream.write(data)
				if ch=='\x07':
					if end<len(text)-1 and not text[end+2].isspace():self.write_line_break();self.write_indent();end+=2
					else:raise EmitterError('unexcpected fold indicator \\a before space')
				if ch is _B:self.write_line_break()
				start=end
			if ch is not _B:breaks=ch in _F;spaces=ch==_D
			end+=1
	def write_literal(self,text,comment=_B):
		hints,_indent,_indicator=self.determine_block_hints(text);self.write_indicator('|'+hints,_A)
		try:
			comment=comment[1][0]
			if comment:self.stream.write(comment)
		except(TypeError,IndexError):pass
		if _indicator=='+':self.open_ended=_A
		self.write_line_break();breaks=_A;start=end=0
		while end<=len(text):
			ch=_B
			if end<len(text):ch=text[end]
			if breaks:
				if ch is _B or ch not in _F:
					for br in text[start:end]:
						if br==_E:self.write_line_break()
						else:self.write_line_break(br)
					if ch is not _B:
						if self.root_context:idnx=self.indent if self.indent is not _B else 0;self.stream.write(_D*(_indent+idnx))
						else:self.write_indent()
					start=end
			elif ch is _B or ch in _F:
				data=text[start:end]
				if bool(self.encoding):data=data.encode(self.encoding)
				self.stream.write(data)
				if ch is _B:self.write_line_break()
				start=end
			if ch is not _B:breaks=ch in _F
			end+=1
	def write_plain(self,text,split=_A):
		if self.root_context:
			if self.requested_indent is not _B:
				self.write_line_break()
				if self.requested_indent!=0:self.write_indent()
			else:self.open_ended=_A
		if not text:return
		if not self.whitespace:
			data=_D;self.column+=len(data)
			if self.encoding:data=data.encode(self.encoding)
			self.stream.write(data)
		self.whitespace=_C;self.indention=_C;spaces=_C;breaks=_C;start=end=0
		while end<=len(text):
			ch=_B
			if end<len(text):ch=text[end]
			if spaces:
				if ch!=_D:
					if start+1==end and self.column>self.best_width and split:self.write_indent();self.whitespace=_C;self.indention=_C
					else:
						data=text[start:end];self.column+=len(data)
						if self.encoding:data=data.encode(self.encoding)
						self.stream.write(data)
					start=end
			elif breaks:
				if ch not in _F:
					if text[start]==_E:self.write_line_break()
					for br in text[start:end]:
						if br==_E:self.write_line_break()
						else:self.write_line_break(br)
					self.write_indent();self.whitespace=_C;self.indention=_C;start=end
			elif ch is _B or ch in _N:
				data=text[start:end];self.column+=len(data)
				if self.encoding:data=data.encode(self.encoding)
				try:self.stream.write(data)
				except:sys.stdout.write(repr(data)+_E);raise
				start=end
			if ch is not _B:spaces=ch==_D;breaks=ch in _F
			end+=1
	def write_comment(self,comment,pre=_C):
		value=comment.value
		if not pre and value[-1]==_E:value=value[:-1]
		try:
			col=comment.start_mark.column
			if comment.value and comment.value.startswith(_E):col=self.column
			elif col<self.column+1:ValueError
		except ValueError:col=self.column+1
		try:
			nr_spaces=col-self.column
			if self.column and value.strip()and nr_spaces<1 and value[0]!=_E:nr_spaces=1
			value=_D*nr_spaces+value
			try:
				if bool(self.encoding):value=value.encode(self.encoding)
			except UnicodeDecodeError:pass
			self.stream.write(value)
		except TypeError:raise
		if not pre:self.write_line_break()
	def write_pre_comment(self,event):
		comments=event.comment[1]
		if comments is _B:return _C
		try:
			start_events=MappingStartEvent,SequenceStartEvent
			for comment in comments:
				if isinstance(event,start_events)and getattr(comment,'pre_done',_B):continue
				if self.column!=0:self.write_line_break()
				self.write_comment(comment,pre=_A)
				if isinstance(event,start_events):comment.pre_done=_A
		except TypeError:sys.stdout.write('eventtt {} {}'.format(type(event),event));raise
		return _A
	def write_post_comment(self,event):
		if self.event.comment[0]is _B:return _C
		comment=event.comment[0];self.write_comment(comment);return _A
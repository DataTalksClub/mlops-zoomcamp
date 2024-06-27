from __future__ import absolute_import
_D='expected <block end>, but found %r'
_C=True
_B=False
_A=None
from.error import MarkedYAMLError
from.tokens import*
from.events import*
from.scanner import Scanner,RoundTripScanner,ScannerError
from.compat import utf8,nprint,nprintf
if _B:from typing import Any,Dict,Optional,List
__all__=['Parser','RoundTripParser','ParserError']
class ParserError(MarkedYAMLError):0
class Parser:
	DEFAULT_TAGS={'!':'!','!!':'tag:yaml.org,2002:'}
	def __init__(self,loader):
		self.loader=loader
		if self.loader is not _A and getattr(self.loader,'_parser',_A)is _A:self.loader._parser=self
		self.reset_parser()
	def reset_parser(self):self.current_event=_A;self.tag_handles={};self.states=[];self.marks=[];self.state=self.parse_stream_start
	def dispose(self):self.reset_parser()
	@property
	def scanner(self):
		if hasattr(self.loader,'typ'):return self.loader.scanner
		return self.loader._scanner
	@property
	def resolver(self):
		if hasattr(self.loader,'typ'):return self.loader.resolver
		return self.loader._resolver
	def check_event(self,*choices):
		if self.current_event is _A:
			if self.state:self.current_event=self.state()
		if self.current_event is not _A:
			if not choices:return _C
			for choice in choices:
				if isinstance(self.current_event,choice):return _C
		return _B
	def peek_event(self):
		if self.current_event is _A:
			if self.state:self.current_event=self.state()
		return self.current_event
	def get_event(self):
		if self.current_event is _A:
			if self.state:self.current_event=self.state()
		value=self.current_event;self.current_event=_A;return value
	def parse_stream_start(self):token=self.scanner.get_token();token.move_comment(self.scanner.peek_token());event=StreamStartEvent(token.start_mark,token.end_mark,encoding=token.encoding);self.state=self.parse_implicit_document_start;return event
	def parse_implicit_document_start(self):
		if not self.scanner.check_token(DirectiveToken,DocumentStartToken,StreamEndToken):self.tag_handles=self.DEFAULT_TAGS;token=self.scanner.peek_token();start_mark=end_mark=token.start_mark;event=DocumentStartEvent(start_mark,end_mark,explicit=_B);self.states.append(self.parse_document_end);self.state=self.parse_block_node;return event
		else:return self.parse_document_start()
	def parse_document_start(self):
		while self.scanner.check_token(DocumentEndToken):self.scanner.get_token()
		if not self.scanner.check_token(StreamEndToken):
			token=self.scanner.peek_token();start_mark=token.start_mark;version,tags=self.process_directives()
			if not self.scanner.check_token(DocumentStartToken):raise ParserError(_A,_A,"expected '<document start>', but found %r"%self.scanner.peek_token().id,self.scanner.peek_token().start_mark)
			token=self.scanner.get_token();end_mark=token.end_mark;event=DocumentStartEvent(start_mark,end_mark,explicit=_C,version=version,tags=tags);self.states.append(self.parse_document_end);self.state=self.parse_document_content
		else:token=self.scanner.get_token();event=StreamEndEvent(token.start_mark,token.end_mark,comment=token.comment);assert not self.states;assert not self.marks;self.state=_A
		return event
	def parse_document_end(self):
		token=self.scanner.peek_token();start_mark=end_mark=token.start_mark;explicit=_B
		if self.scanner.check_token(DocumentEndToken):token=self.scanner.get_token();end_mark=token.end_mark;explicit=_C
		event=DocumentEndEvent(start_mark,end_mark,explicit=explicit)
		if self.resolver.processing_version==(1,1):self.state=self.parse_document_start
		else:self.state=self.parse_implicit_document_start
		return event
	def parse_document_content(self):
		if self.scanner.check_token(DirectiveToken,DocumentStartToken,DocumentEndToken,StreamEndToken):event=self.process_empty_scalar(self.scanner.peek_token().start_mark);self.state=self.states.pop();return event
		else:return self.parse_block_node()
	def process_directives(self):
		yaml_version=_A;self.tag_handles={}
		while self.scanner.check_token(DirectiveToken):
			token=self.scanner.get_token()
			if token.name=='YAML':
				if yaml_version is not _A:raise ParserError(_A,_A,'found duplicate YAML directive',token.start_mark)
				major,minor=token.value
				if major!=1:raise ParserError(_A,_A,'found incompatible YAML document (version 1.* is required)',token.start_mark)
				yaml_version=token.value
			elif token.name=='TAG':
				handle,prefix=token.value
				if handle in self.tag_handles:raise ParserError(_A,_A,'duplicate tag handle %r'%utf8(handle),token.start_mark)
				self.tag_handles[handle]=prefix
		if bool(self.tag_handles):value=yaml_version,self.tag_handles.copy()
		else:value=yaml_version,_A
		if self.loader is not _A and hasattr(self.loader,'tags'):
			self.loader.version=yaml_version
			if self.loader.tags is _A:self.loader.tags={}
			for k in self.tag_handles:self.loader.tags[k]=self.tag_handles[k]
		for key in self.DEFAULT_TAGS:
			if key not in self.tag_handles:self.tag_handles[key]=self.DEFAULT_TAGS[key]
		return value
	def parse_block_node(self):return self.parse_node(block=_C)
	def parse_flow_node(self):return self.parse_node()
	def parse_block_node_or_indentless_sequence(self):return self.parse_node(block=_C,indentless_sequence=_C)
	def transform_tag(self,handle,suffix):return self.tag_handles[handle]+suffix
	def parse_node(self,block=_B,indentless_sequence=_B):
		if self.scanner.check_token(AliasToken):token=self.scanner.get_token();event=AliasEvent(token.value,token.start_mark,token.end_mark);self.state=self.states.pop();return event
		anchor=_A;tag=_A;start_mark=end_mark=tag_mark=_A
		if self.scanner.check_token(AnchorToken):
			token=self.scanner.get_token();start_mark=token.start_mark;end_mark=token.end_mark;anchor=token.value
			if self.scanner.check_token(TagToken):token=self.scanner.get_token();tag_mark=token.start_mark;end_mark=token.end_mark;tag=token.value
		elif self.scanner.check_token(TagToken):
			token=self.scanner.get_token();start_mark=tag_mark=token.start_mark;end_mark=token.end_mark;tag=token.value
			if self.scanner.check_token(AnchorToken):token=self.scanner.get_token();start_mark=tag_mark=token.start_mark;end_mark=token.end_mark;anchor=token.value
		if tag is not _A:
			handle,suffix=tag
			if handle is not _A:
				if handle not in self.tag_handles:raise ParserError('while parsing a node',start_mark,'found undefined tag handle %r'%utf8(handle),tag_mark)
				tag=self.transform_tag(handle,suffix)
			else:tag=suffix
		if start_mark is _A:start_mark=end_mark=self.scanner.peek_token().start_mark
		event=_A;implicit=tag is _A or tag=='!'
		if indentless_sequence and self.scanner.check_token(BlockEntryToken):
			comment=_A;pt=self.scanner.peek_token()
			if pt.comment and pt.comment[0]:comment=[pt.comment[0],[]];pt.comment[0]=_A
			end_mark=self.scanner.peek_token().end_mark;event=SequenceStartEvent(anchor,tag,implicit,start_mark,end_mark,flow_style=_B,comment=comment);self.state=self.parse_indentless_sequence_entry;return event
		if self.scanner.check_token(ScalarToken):
			token=self.scanner.get_token();end_mark=token.end_mark
			if token.plain and tag is _A or tag=='!':implicit=_C,_B
			elif tag is _A:implicit=_B,_C
			else:implicit=_B,_B
			event=ScalarEvent(anchor,tag,implicit,token.value,start_mark,end_mark,style=token.style,comment=token.comment);self.state=self.states.pop()
		elif self.scanner.check_token(FlowSequenceStartToken):pt=self.scanner.peek_token();end_mark=pt.end_mark;event=SequenceStartEvent(anchor,tag,implicit,start_mark,end_mark,flow_style=_C,comment=pt.comment);self.state=self.parse_flow_sequence_first_entry
		elif self.scanner.check_token(FlowMappingStartToken):pt=self.scanner.peek_token();end_mark=pt.end_mark;event=MappingStartEvent(anchor,tag,implicit,start_mark,end_mark,flow_style=_C,comment=pt.comment);self.state=self.parse_flow_mapping_first_key
		elif block and self.scanner.check_token(BlockSequenceStartToken):
			end_mark=self.scanner.peek_token().start_mark;pt=self.scanner.peek_token();comment=pt.comment
			if comment is _A or comment[1]is _A:comment=pt.split_comment()
			event=SequenceStartEvent(anchor,tag,implicit,start_mark,end_mark,flow_style=_B,comment=comment);self.state=self.parse_block_sequence_first_entry
		elif block and self.scanner.check_token(BlockMappingStartToken):end_mark=self.scanner.peek_token().start_mark;comment=self.scanner.peek_token().comment;event=MappingStartEvent(anchor,tag,implicit,start_mark,end_mark,flow_style=_B,comment=comment);self.state=self.parse_block_mapping_first_key
		elif anchor is not _A or tag is not _A:event=ScalarEvent(anchor,tag,(implicit,_B),'',start_mark,end_mark);self.state=self.states.pop()
		else:
			if block:node='block'
			else:node='flow'
			token=self.scanner.peek_token();raise ParserError('while parsing a %s node'%node,start_mark,'expected the node content, but found %r'%token.id,token.start_mark)
		return event
	def parse_block_sequence_first_entry(self):token=self.scanner.get_token();self.marks.append(token.start_mark);return self.parse_block_sequence_entry()
	def parse_block_sequence_entry(self):
		if self.scanner.check_token(BlockEntryToken):
			token=self.scanner.get_token();token.move_comment(self.scanner.peek_token())
			if not self.scanner.check_token(BlockEntryToken,BlockEndToken):self.states.append(self.parse_block_sequence_entry);return self.parse_block_node()
			else:self.state=self.parse_block_sequence_entry;return self.process_empty_scalar(token.end_mark)
		if not self.scanner.check_token(BlockEndToken):token=self.scanner.peek_token();raise ParserError('while parsing a block collection',self.marks[-1],_D%token.id,token.start_mark)
		token=self.scanner.get_token();event=SequenceEndEvent(token.start_mark,token.end_mark,comment=token.comment);self.state=self.states.pop();self.marks.pop();return event
	def parse_indentless_sequence_entry(self):
		if self.scanner.check_token(BlockEntryToken):
			token=self.scanner.get_token();token.move_comment(self.scanner.peek_token())
			if not self.scanner.check_token(BlockEntryToken,KeyToken,ValueToken,BlockEndToken):self.states.append(self.parse_indentless_sequence_entry);return self.parse_block_node()
			else:self.state=self.parse_indentless_sequence_entry;return self.process_empty_scalar(token.end_mark)
		token=self.scanner.peek_token();event=SequenceEndEvent(token.start_mark,token.start_mark,comment=token.comment);self.state=self.states.pop();return event
	def parse_block_mapping_first_key(self):token=self.scanner.get_token();self.marks.append(token.start_mark);return self.parse_block_mapping_key()
	def parse_block_mapping_key(self):
		if self.scanner.check_token(KeyToken):
			token=self.scanner.get_token();token.move_comment(self.scanner.peek_token())
			if not self.scanner.check_token(KeyToken,ValueToken,BlockEndToken):self.states.append(self.parse_block_mapping_value);return self.parse_block_node_or_indentless_sequence()
			else:self.state=self.parse_block_mapping_value;return self.process_empty_scalar(token.end_mark)
		if self.resolver.processing_version>(1,1)and self.scanner.check_token(ValueToken):self.state=self.parse_block_mapping_value;return self.process_empty_scalar(self.scanner.peek_token().start_mark)
		if not self.scanner.check_token(BlockEndToken):token=self.scanner.peek_token();raise ParserError('while parsing a block mapping',self.marks[-1],_D%token.id,token.start_mark)
		token=self.scanner.get_token();token.move_comment(self.scanner.peek_token());event=MappingEndEvent(token.start_mark,token.end_mark,comment=token.comment);self.state=self.states.pop();self.marks.pop();return event
	def parse_block_mapping_value(self):
		if self.scanner.check_token(ValueToken):
			token=self.scanner.get_token()
			if self.scanner.check_token(ValueToken):token.move_comment(self.scanner.peek_token())
			elif not self.scanner.check_token(KeyToken):token.move_comment(self.scanner.peek_token(),empty=_C)
			if not self.scanner.check_token(KeyToken,ValueToken,BlockEndToken):self.states.append(self.parse_block_mapping_key);return self.parse_block_node_or_indentless_sequence()
			else:
				self.state=self.parse_block_mapping_key;comment=token.comment
				if comment is _A:
					token=self.scanner.peek_token();comment=token.comment
					if comment:token._comment=[_A,comment[1]];comment=[comment[0],_A]
				return self.process_empty_scalar(token.end_mark,comment=comment)
		else:self.state=self.parse_block_mapping_key;token=self.scanner.peek_token();return self.process_empty_scalar(token.start_mark)
	def parse_flow_sequence_first_entry(self):token=self.scanner.get_token();self.marks.append(token.start_mark);return self.parse_flow_sequence_entry(first=_C)
	def parse_flow_sequence_entry(self,first=_B):
		if not self.scanner.check_token(FlowSequenceEndToken):
			if not first:
				if self.scanner.check_token(FlowEntryToken):self.scanner.get_token()
				else:token=self.scanner.peek_token();raise ParserError('while parsing a flow sequence',self.marks[-1],"expected ',' or ']', but got %r"%token.id,token.start_mark)
			if self.scanner.check_token(KeyToken):token=self.scanner.peek_token();event=MappingStartEvent(_A,_A,_C,token.start_mark,token.end_mark,flow_style=_C);self.state=self.parse_flow_sequence_entry_mapping_key;return event
			elif not self.scanner.check_token(FlowSequenceEndToken):self.states.append(self.parse_flow_sequence_entry);return self.parse_flow_node()
		token=self.scanner.get_token();event=SequenceEndEvent(token.start_mark,token.end_mark,comment=token.comment);self.state=self.states.pop();self.marks.pop();return event
	def parse_flow_sequence_entry_mapping_key(self):
		token=self.scanner.get_token()
		if not self.scanner.check_token(ValueToken,FlowEntryToken,FlowSequenceEndToken):self.states.append(self.parse_flow_sequence_entry_mapping_value);return self.parse_flow_node()
		else:self.state=self.parse_flow_sequence_entry_mapping_value;return self.process_empty_scalar(token.end_mark)
	def parse_flow_sequence_entry_mapping_value(self):
		if self.scanner.check_token(ValueToken):
			token=self.scanner.get_token()
			if not self.scanner.check_token(FlowEntryToken,FlowSequenceEndToken):self.states.append(self.parse_flow_sequence_entry_mapping_end);return self.parse_flow_node()
			else:self.state=self.parse_flow_sequence_entry_mapping_end;return self.process_empty_scalar(token.end_mark)
		else:self.state=self.parse_flow_sequence_entry_mapping_end;token=self.scanner.peek_token();return self.process_empty_scalar(token.start_mark)
	def parse_flow_sequence_entry_mapping_end(self):self.state=self.parse_flow_sequence_entry;token=self.scanner.peek_token();return MappingEndEvent(token.start_mark,token.start_mark)
	def parse_flow_mapping_first_key(self):token=self.scanner.get_token();self.marks.append(token.start_mark);return self.parse_flow_mapping_key(first=_C)
	def parse_flow_mapping_key(self,first=_B):
		if not self.scanner.check_token(FlowMappingEndToken):
			if not first:
				if self.scanner.check_token(FlowEntryToken):self.scanner.get_token()
				else:token=self.scanner.peek_token();raise ParserError('while parsing a flow mapping',self.marks[-1],"expected ',' or '}', but got %r"%token.id,token.start_mark)
			if self.scanner.check_token(KeyToken):
				token=self.scanner.get_token()
				if not self.scanner.check_token(ValueToken,FlowEntryToken,FlowMappingEndToken):self.states.append(self.parse_flow_mapping_value);return self.parse_flow_node()
				else:self.state=self.parse_flow_mapping_value;return self.process_empty_scalar(token.end_mark)
			elif self.resolver.processing_version>(1,1)and self.scanner.check_token(ValueToken):self.state=self.parse_flow_mapping_value;return self.process_empty_scalar(self.scanner.peek_token().end_mark)
			elif not self.scanner.check_token(FlowMappingEndToken):self.states.append(self.parse_flow_mapping_empty_value);return self.parse_flow_node()
		token=self.scanner.get_token();event=MappingEndEvent(token.start_mark,token.end_mark,comment=token.comment);self.state=self.states.pop();self.marks.pop();return event
	def parse_flow_mapping_value(self):
		if self.scanner.check_token(ValueToken):
			token=self.scanner.get_token()
			if not self.scanner.check_token(FlowEntryToken,FlowMappingEndToken):self.states.append(self.parse_flow_mapping_key);return self.parse_flow_node()
			else:self.state=self.parse_flow_mapping_key;return self.process_empty_scalar(token.end_mark)
		else:self.state=self.parse_flow_mapping_key;token=self.scanner.peek_token();return self.process_empty_scalar(token.start_mark)
	def parse_flow_mapping_empty_value(self):self.state=self.parse_flow_mapping_key;return self.process_empty_scalar(self.scanner.peek_token().start_mark)
	def process_empty_scalar(self,mark,comment=_A):return ScalarEvent(_A,_A,(_C,_B),'',mark,mark,comment=comment)
class RoundTripParser(Parser):
	def transform_tag(self,handle,suffix):
		if handle=='!!'and suffix in('null','bool','int','float','binary','timestamp','omap','pairs','set','str','seq','map'):return Parser.transform_tag(self,handle,suffix)
		return handle+suffix
from __future__ import print_function,absolute_import,division,unicode_literals
_b='\u2028\u2029'
_a='\r\n\x85'
_Z='while scanning a quoted scalar'
_Y='0123456789ABCDEFabcdef'
_X=' \r\n\x85\u2028\u2029'
_W='expected a comment or a line break, but found %r'
_V='directive'
_U='\ufeff'
_T="could not find expected ':'"
_S='while scanning a simple key'
_R="expected ' ', but found %r"
_Q='while scanning a %s'
_P='\r\n\x85\u2028\u2029'
_O='while scanning a block scalar'
_N='expected alphabetic or numeric character, but found %r'
_M='...'
_L='---'
_K=' \t'
_J='\x00 \r\n\x85\u2028\u2029'
_I='\x00'
_H='!'
_G='while scanning a directive'
_F='#'
_E='\n'
_D=' '
_C=None
_B=False
_A=True
from.error import MarkedYAMLError
from.tokens import*
from.compat import utf8,unichr,PY3,check_anchorname_char,nprint
if _B:from typing import Any,Dict,Optional,List,Union,Text;from.compat import VersionType
__all__=['Scanner','RoundTripScanner','ScannerError']
_THE_END='\n\x00\r\x85\u2028\u2029'
_THE_END_SPACE_TAB=' \n\x00\t\r\x85\u2028\u2029'
_SPACE_TAB=_K
class ScannerError(MarkedYAMLError):0
class SimpleKey:
	def __init__(self,token_number,required,index,line,column,mark):self.token_number=token_number;self.required=required;self.index=index;self.line=line;self.column=column;self.mark=mark
class Scanner:
	def __init__(self,loader=_C):
		self.loader=loader
		if self.loader is not _C and getattr(self.loader,'_scanner',_C)is _C:self.loader._scanner=self
		self.reset_scanner();self.first_time=_B;self.yaml_version=_C
	@property
	def flow_level(self):return len(self.flow_context)
	def reset_scanner(self):self.done=_B;self.flow_context=[];self.tokens=[];self.fetch_stream_start();self.tokens_taken=0;self.indent=-1;self.indents=[];self.allow_simple_key=_A;self.possible_simple_keys={}
	@property
	def reader(self):
		try:return self._scanner_reader
		except AttributeError:
			if hasattr(self.loader,'typ'):self._scanner_reader=self.loader.reader
			else:self._scanner_reader=self.loader._reader
			return self._scanner_reader
	@property
	def scanner_processing_version(self):
		if hasattr(self.loader,'typ'):return self.loader.resolver.processing_version
		return self.loader.processing_version
	def check_token(self,*choices):
		while self.need_more_tokens():self.fetch_more_tokens()
		if bool(self.tokens):
			if not choices:return _A
			for choice in choices:
				if isinstance(self.tokens[0],choice):return _A
		return _B
	def peek_token(self):
		while self.need_more_tokens():self.fetch_more_tokens()
		if bool(self.tokens):return self.tokens[0]
	def get_token(self):
		while self.need_more_tokens():self.fetch_more_tokens()
		if bool(self.tokens):self.tokens_taken+=1;return self.tokens.pop(0)
	def need_more_tokens(self):
		if self.done:return _B
		if not self.tokens:return _A
		self.stale_possible_simple_keys()
		if self.next_possible_simple_key()==self.tokens_taken:return _A
		return _B
	def fetch_comment(self,comment):raise NotImplementedError
	def fetch_more_tokens(self):
		comment=self.scan_to_next_token()
		if comment is not _C:return self.fetch_comment(comment)
		self.stale_possible_simple_keys();self.unwind_indent(self.reader.column);ch=self.reader.peek()
		if ch==_I:return self.fetch_stream_end()
		if ch=='%'and self.check_directive():return self.fetch_directive()
		if ch=='-'and self.check_document_start():return self.fetch_document_start()
		if ch=='.'and self.check_document_end():return self.fetch_document_end()
		if ch=='[':return self.fetch_flow_sequence_start()
		if ch=='{':return self.fetch_flow_mapping_start()
		if ch==']':return self.fetch_flow_sequence_end()
		if ch=='}':return self.fetch_flow_mapping_end()
		if ch==',':return self.fetch_flow_entry()
		if ch=='-'and self.check_block_entry():return self.fetch_block_entry()
		if ch=='?'and self.check_key():return self.fetch_key()
		if ch==':'and self.check_value():return self.fetch_value()
		if ch=='*':return self.fetch_alias()
		if ch=='&':return self.fetch_anchor()
		if ch==_H:return self.fetch_tag()
		if ch=='|'and not self.flow_level:return self.fetch_literal()
		if ch=='>'and not self.flow_level:return self.fetch_folded()
		if ch=="'":return self.fetch_single()
		if ch=='"':return self.fetch_double()
		if self.check_plain():return self.fetch_plain()
		raise ScannerError('while scanning for the next token',_C,'found character %r that cannot start any token'%utf8(ch),self.reader.get_mark())
	def next_possible_simple_key(self):
		min_token_number=_C
		for level in self.possible_simple_keys:
			key=self.possible_simple_keys[level]
			if min_token_number is _C or key.token_number<min_token_number:min_token_number=key.token_number
		return min_token_number
	def stale_possible_simple_keys(self):
		for level in list(self.possible_simple_keys):
			key=self.possible_simple_keys[level]
			if key.line!=self.reader.line or self.reader.index-key.index>1024:
				if key.required:raise ScannerError(_S,key.mark,_T,self.reader.get_mark())
				del self.possible_simple_keys[level]
	def save_possible_simple_key(self):
		required=not self.flow_level and self.indent==self.reader.column
		if self.allow_simple_key:self.remove_possible_simple_key();token_number=self.tokens_taken+len(self.tokens);key=SimpleKey(token_number,required,self.reader.index,self.reader.line,self.reader.column,self.reader.get_mark());self.possible_simple_keys[self.flow_level]=key
	def remove_possible_simple_key(self):
		if self.flow_level in self.possible_simple_keys:
			key=self.possible_simple_keys[self.flow_level]
			if key.required:raise ScannerError(_S,key.mark,_T,self.reader.get_mark())
			del self.possible_simple_keys[self.flow_level]
	def unwind_indent(self,column):
		if bool(self.flow_level):return
		while self.indent>column:mark=self.reader.get_mark();self.indent=self.indents.pop();self.tokens.append(BlockEndToken(mark,mark))
	def add_indent(self,column):
		if self.indent<column:self.indents.append(self.indent);self.indent=column;return _A
		return _B
	def fetch_stream_start(self):mark=self.reader.get_mark();self.tokens.append(StreamStartToken(mark,mark,encoding=self.reader.encoding))
	def fetch_stream_end(self):self.unwind_indent(-1);self.remove_possible_simple_key();self.allow_simple_key=_B;self.possible_simple_keys={};mark=self.reader.get_mark();self.tokens.append(StreamEndToken(mark,mark));self.done=_A
	def fetch_directive(self):self.unwind_indent(-1);self.remove_possible_simple_key();self.allow_simple_key=_B;self.tokens.append(self.scan_directive())
	def fetch_document_start(self):self.fetch_document_indicator(DocumentStartToken)
	def fetch_document_end(self):self.fetch_document_indicator(DocumentEndToken)
	def fetch_document_indicator(self,TokenClass):self.unwind_indent(-1);self.remove_possible_simple_key();self.allow_simple_key=_B;start_mark=self.reader.get_mark();self.reader.forward(3);end_mark=self.reader.get_mark();self.tokens.append(TokenClass(start_mark,end_mark))
	def fetch_flow_sequence_start(self):self.fetch_flow_collection_start(FlowSequenceStartToken,to_push='[')
	def fetch_flow_mapping_start(self):self.fetch_flow_collection_start(FlowMappingStartToken,to_push='{')
	def fetch_flow_collection_start(self,TokenClass,to_push):self.save_possible_simple_key();self.flow_context.append(to_push);self.allow_simple_key=_A;start_mark=self.reader.get_mark();self.reader.forward();end_mark=self.reader.get_mark();self.tokens.append(TokenClass(start_mark,end_mark))
	def fetch_flow_sequence_end(self):self.fetch_flow_collection_end(FlowSequenceEndToken)
	def fetch_flow_mapping_end(self):self.fetch_flow_collection_end(FlowMappingEndToken)
	def fetch_flow_collection_end(self,TokenClass):
		self.remove_possible_simple_key()
		try:popped=self.flow_context.pop()
		except IndexError:pass
		self.allow_simple_key=_B;start_mark=self.reader.get_mark();self.reader.forward();end_mark=self.reader.get_mark();self.tokens.append(TokenClass(start_mark,end_mark))
	def fetch_flow_entry(self):self.allow_simple_key=_A;self.remove_possible_simple_key();start_mark=self.reader.get_mark();self.reader.forward();end_mark=self.reader.get_mark();self.tokens.append(FlowEntryToken(start_mark,end_mark))
	def fetch_block_entry(self):
		if not self.flow_level:
			if not self.allow_simple_key:raise ScannerError(_C,_C,'sequence entries are not allowed here',self.reader.get_mark())
			if self.add_indent(self.reader.column):mark=self.reader.get_mark();self.tokens.append(BlockSequenceStartToken(mark,mark))
		else:0
		self.allow_simple_key=_A;self.remove_possible_simple_key();start_mark=self.reader.get_mark();self.reader.forward();end_mark=self.reader.get_mark();self.tokens.append(BlockEntryToken(start_mark,end_mark))
	def fetch_key(self):
		if not self.flow_level:
			if not self.allow_simple_key:raise ScannerError(_C,_C,'mapping keys are not allowed here',self.reader.get_mark())
			if self.add_indent(self.reader.column):mark=self.reader.get_mark();self.tokens.append(BlockMappingStartToken(mark,mark))
		self.allow_simple_key=not self.flow_level;self.remove_possible_simple_key();start_mark=self.reader.get_mark();self.reader.forward();end_mark=self.reader.get_mark();self.tokens.append(KeyToken(start_mark,end_mark))
	def fetch_value(self):
		if self.flow_level in self.possible_simple_keys:
			key=self.possible_simple_keys[self.flow_level];del self.possible_simple_keys[self.flow_level];self.tokens.insert(key.token_number-self.tokens_taken,KeyToken(key.mark,key.mark))
			if not self.flow_level:
				if self.add_indent(key.column):self.tokens.insert(key.token_number-self.tokens_taken,BlockMappingStartToken(key.mark,key.mark))
			self.allow_simple_key=_B
		else:
			if not self.flow_level:
				if not self.allow_simple_key:raise ScannerError(_C,_C,'mapping values are not allowed here',self.reader.get_mark())
			if not self.flow_level:
				if self.add_indent(self.reader.column):mark=self.reader.get_mark();self.tokens.append(BlockMappingStartToken(mark,mark))
			self.allow_simple_key=not self.flow_level;self.remove_possible_simple_key()
		start_mark=self.reader.get_mark();self.reader.forward();end_mark=self.reader.get_mark();self.tokens.append(ValueToken(start_mark,end_mark))
	def fetch_alias(self):self.save_possible_simple_key();self.allow_simple_key=_B;self.tokens.append(self.scan_anchor(AliasToken))
	def fetch_anchor(self):self.save_possible_simple_key();self.allow_simple_key=_B;self.tokens.append(self.scan_anchor(AnchorToken))
	def fetch_tag(self):self.save_possible_simple_key();self.allow_simple_key=_B;self.tokens.append(self.scan_tag())
	def fetch_literal(self):self.fetch_block_scalar(style='|')
	def fetch_folded(self):self.fetch_block_scalar(style='>')
	def fetch_block_scalar(self,style):self.allow_simple_key=_A;self.remove_possible_simple_key();self.tokens.append(self.scan_block_scalar(style))
	def fetch_single(self):self.fetch_flow_scalar(style="'")
	def fetch_double(self):self.fetch_flow_scalar(style='"')
	def fetch_flow_scalar(self,style):self.save_possible_simple_key();self.allow_simple_key=_B;self.tokens.append(self.scan_flow_scalar(style))
	def fetch_plain(self):self.save_possible_simple_key();self.allow_simple_key=_B;self.tokens.append(self.scan_plain())
	def check_directive(self):
		if self.reader.column==0:return _A
	def check_document_start(self):
		if self.reader.column==0:
			if self.reader.prefix(3)==_L and self.reader.peek(3)in _THE_END_SPACE_TAB:return _A
	def check_document_end(self):
		if self.reader.column==0:
			if self.reader.prefix(3)==_M and self.reader.peek(3)in _THE_END_SPACE_TAB:return _A
	def check_block_entry(self):return self.reader.peek(1)in _THE_END_SPACE_TAB
	def check_key(self):
		if bool(self.flow_level):return _A
		return self.reader.peek(1)in _THE_END_SPACE_TAB
	def check_value(self):
		if self.scanner_processing_version==(1,1):
			if bool(self.flow_level):return _A
		elif bool(self.flow_level):
			if self.flow_context[-1]=='[':
				if self.reader.peek(1)not in _THE_END_SPACE_TAB:return _B
			elif self.tokens and isinstance(self.tokens[-1],ValueToken):
				if self.reader.peek(1)not in _THE_END_SPACE_TAB:return _B
			return _A
		return self.reader.peek(1)in _THE_END_SPACE_TAB
	def check_plain(self):
		A='\x00 \t\r\n\x85\u2028\u2029-?:,[]{}#&*!|>\'"%@`';srp=self.reader.peek;ch=srp()
		if self.scanner_processing_version==(1,1):return ch not in A or srp(1)not in _THE_END_SPACE_TAB and(ch=='-'or not self.flow_level and ch in'?:')
		if ch not in A:return _A
		ch1=srp(1)
		if ch=='-'and ch1 not in _THE_END_SPACE_TAB:return _A
		if ch==':'and bool(self.flow_level)and ch1 not in _SPACE_TAB:return _A
		return srp(1)not in _THE_END_SPACE_TAB and(ch=='-'or not self.flow_level and ch in'?:')
	def scan_to_next_token(self):
		srp=self.reader.peek;srf=self.reader.forward
		if self.reader.index==0 and srp()==_U:srf()
		found=_B;_the_end=_THE_END
		while not found:
			while srp()==_D:srf()
			if srp()==_F:
				while srp()not in _the_end:srf()
			if self.scan_line_break():
				if not self.flow_level:self.allow_simple_key=_A
			else:found=_A
	def scan_directive(self):
		srp=self.reader.peek;srf=self.reader.forward;start_mark=self.reader.get_mark();srf();name=self.scan_directive_name(start_mark);value=_C
		if name=='YAML':value=self.scan_yaml_directive_value(start_mark);end_mark=self.reader.get_mark()
		elif name=='TAG':value=self.scan_tag_directive_value(start_mark);end_mark=self.reader.get_mark()
		else:
			end_mark=self.reader.get_mark()
			while srp()not in _THE_END:srf()
		self.scan_directive_ignored_line(start_mark);return DirectiveToken(name,value,start_mark,end_mark)
	def scan_directive_name(self,start_mark):
		length=0;srp=self.reader.peek;ch=srp(length)
		while'0'<=ch<='9'or'A'<=ch<='Z'or'a'<=ch<='z'or ch in'-_:.':length+=1;ch=srp(length)
		if not length:raise ScannerError(_G,start_mark,_N%utf8(ch),self.reader.get_mark())
		value=self.reader.prefix(length);self.reader.forward(length);ch=srp()
		if ch not in _J:raise ScannerError(_G,start_mark,_N%utf8(ch),self.reader.get_mark())
		return value
	def scan_yaml_directive_value(self,start_mark):
		srp=self.reader.peek;srf=self.reader.forward
		while srp()==_D:srf()
		major=self.scan_yaml_directive_number(start_mark)
		if srp()!='.':raise ScannerError(_G,start_mark,"expected a digit or '.', but found %r"%utf8(srp()),self.reader.get_mark())
		srf();minor=self.scan_yaml_directive_number(start_mark)
		if srp()not in _J:raise ScannerError(_G,start_mark,"expected a digit or ' ', but found %r"%utf8(srp()),self.reader.get_mark())
		self.yaml_version=major,minor;return self.yaml_version
	def scan_yaml_directive_number(self,start_mark):
		srp=self.reader.peek;srf=self.reader.forward;ch=srp()
		if not'0'<=ch<='9':raise ScannerError(_G,start_mark,'expected a digit, but found %r'%utf8(ch),self.reader.get_mark())
		length=0
		while'0'<=srp(length)<='9':length+=1
		value=int(self.reader.prefix(length));srf(length);return value
	def scan_tag_directive_value(self,start_mark):
		srp=self.reader.peek;srf=self.reader.forward
		while srp()==_D:srf()
		handle=self.scan_tag_directive_handle(start_mark)
		while srp()==_D:srf()
		prefix=self.scan_tag_directive_prefix(start_mark);return handle,prefix
	def scan_tag_directive_handle(self,start_mark):
		value=self.scan_tag_handle(_V,start_mark);ch=self.reader.peek()
		if ch!=_D:raise ScannerError(_G,start_mark,_R%utf8(ch),self.reader.get_mark())
		return value
	def scan_tag_directive_prefix(self,start_mark):
		value=self.scan_tag_uri(_V,start_mark);ch=self.reader.peek()
		if ch not in _J:raise ScannerError(_G,start_mark,_R%utf8(ch),self.reader.get_mark())
		return value
	def scan_directive_ignored_line(self,start_mark):
		srp=self.reader.peek;srf=self.reader.forward
		while srp()==_D:srf()
		if srp()==_F:
			while srp()not in _THE_END:srf()
		ch=srp()
		if ch not in _THE_END:raise ScannerError(_G,start_mark,_W%utf8(ch),self.reader.get_mark())
		self.scan_line_break()
	def scan_anchor(self,TokenClass):
		A='while scanning an %s';srp=self.reader.peek;start_mark=self.reader.get_mark();indicator=srp()
		if indicator=='*':name='alias'
		else:name='anchor'
		self.reader.forward();length=0;ch=srp(length)
		while check_anchorname_char(ch):length+=1;ch=srp(length)
		if not length:raise ScannerError(A%(name,),start_mark,_N%utf8(ch),self.reader.get_mark())
		value=self.reader.prefix(length);self.reader.forward(length)
		if ch not in'\x00 \t\r\n\x85\u2028\u2029?:,[]{}%@`':raise ScannerError(A%(name,),start_mark,_N%utf8(ch),self.reader.get_mark())
		end_mark=self.reader.get_mark();return TokenClass(value,start_mark,end_mark)
	def scan_tag(self):
		A='tag';srp=self.reader.peek;start_mark=self.reader.get_mark();ch=srp(1)
		if ch=='<':
			handle=_C;self.reader.forward(2);suffix=self.scan_tag_uri(A,start_mark)
			if srp()!='>':raise ScannerError('while parsing a tag',start_mark,"expected '>', but found %r"%utf8(srp()),self.reader.get_mark())
			self.reader.forward()
		elif ch in _THE_END_SPACE_TAB:handle=_C;suffix=_H;self.reader.forward()
		else:
			length=1;use_handle=_B
			while ch not in _J:
				if ch==_H:use_handle=_A;break
				length+=1;ch=srp(length)
			handle=_H
			if use_handle:handle=self.scan_tag_handle(A,start_mark)
			else:handle=_H;self.reader.forward()
			suffix=self.scan_tag_uri(A,start_mark)
		ch=srp()
		if ch not in _J:raise ScannerError('while scanning a tag',start_mark,_R%utf8(ch),self.reader.get_mark())
		value=handle,suffix;end_mark=self.reader.get_mark();return TagToken(value,start_mark,end_mark)
	def scan_block_scalar(self,style,rt=_B):
		srp=self.reader.peek
		if style=='>':folded=_A
		else:folded=_B
		chunks=[];start_mark=self.reader.get_mark();self.reader.forward();chomping,increment=self.scan_block_scalar_indicators(start_mark);block_scalar_comment=self.scan_block_scalar_ignored_line(start_mark);min_indent=self.indent+1
		if increment is _C:
			if min_indent<1 and(style not in'|>'or self.scanner_processing_version==(1,1)and getattr(self.loader,'top_level_block_style_scalar_no_indent_error_1_1',_B)):min_indent=1
			breaks,max_indent,end_mark=self.scan_block_scalar_indentation();indent=max(min_indent,max_indent)
		else:
			if min_indent<1:min_indent=1
			indent=min_indent+increment-1;breaks,end_mark=self.scan_block_scalar_breaks(indent)
		line_break=''
		while self.reader.column==indent and srp()!=_I:
			chunks.extend(breaks);leading_non_space=srp()not in _K;length=0
			while srp(length)not in _THE_END:length+=1
			chunks.append(self.reader.prefix(length));self.reader.forward(length);line_break=self.scan_line_break();breaks,end_mark=self.scan_block_scalar_breaks(indent)
			if style in'|>'and min_indent==0:
				if self.check_document_start()or self.check_document_end():break
			if self.reader.column==indent and srp()!=_I:
				if rt and folded and line_break==_E:chunks.append('\x07')
				if folded and line_break==_E and leading_non_space and srp()not in _K:
					if not breaks:chunks.append(_D)
				else:chunks.append(line_break)
			else:break
		trailing=[]
		if chomping in[_C,_A]:chunks.append(line_break)
		if chomping is _A:chunks.extend(breaks)
		elif chomping in[_C,_B]:trailing.extend(breaks)
		token=ScalarToken(''.join(chunks),_B,start_mark,end_mark,style)
		if block_scalar_comment is not _C:token.add_pre_comments([block_scalar_comment])
		if len(trailing)>0:
			comment=self.scan_to_next_token()
			while comment:trailing.append(_D*comment[1].column+comment[0]);comment=self.scan_to_next_token()
			comment_end_mark=self.reader.get_mark();comment=CommentToken(''.join(trailing),end_mark,comment_end_mark);token.add_post_comment(comment)
		return token
	def scan_block_scalar_indicators(self,start_mark):
		B='expected indentation indicator in the range 1-9, but found 0';A='0123456789';srp=self.reader.peek;chomping=_C;increment=_C;ch=srp()
		if ch in'+-':
			if ch=='+':chomping=_A
			else:chomping=_B
			self.reader.forward();ch=srp()
			if ch in A:
				increment=int(ch)
				if increment==0:raise ScannerError(_O,start_mark,B,self.reader.get_mark())
				self.reader.forward()
		elif ch in A:
			increment=int(ch)
			if increment==0:raise ScannerError(_O,start_mark,B,self.reader.get_mark())
			self.reader.forward();ch=srp()
			if ch in'+-':
				if ch=='+':chomping=_A
				else:chomping=_B
				self.reader.forward()
		ch=srp()
		if ch not in _J:raise ScannerError(_O,start_mark,'expected chomping or indentation indicators, but found %r'%utf8(ch),self.reader.get_mark())
		return chomping,increment
	def scan_block_scalar_ignored_line(self,start_mark):
		srp=self.reader.peek;srf=self.reader.forward;prefix='';comment=_C
		while srp()==_D:prefix+=srp();srf()
		if srp()==_F:
			comment=prefix
			while srp()not in _THE_END:comment+=srp();srf()
		ch=srp()
		if ch not in _THE_END:raise ScannerError(_O,start_mark,_W%utf8(ch),self.reader.get_mark())
		self.scan_line_break();return comment
	def scan_block_scalar_indentation(self):
		srp=self.reader.peek;srf=self.reader.forward;chunks=[];max_indent=0;end_mark=self.reader.get_mark()
		while srp()in _X:
			if srp()!=_D:chunks.append(self.scan_line_break());end_mark=self.reader.get_mark()
			else:
				srf()
				if self.reader.column>max_indent:max_indent=self.reader.column
		return chunks,max_indent,end_mark
	def scan_block_scalar_breaks(self,indent):
		chunks=[];srp=self.reader.peek;srf=self.reader.forward;end_mark=self.reader.get_mark()
		while self.reader.column<indent and srp()==_D:srf()
		while srp()in _P:
			chunks.append(self.scan_line_break());end_mark=self.reader.get_mark()
			while self.reader.column<indent and srp()==_D:srf()
		return chunks,end_mark
	def scan_flow_scalar(self,style):
		if style=='"':double=_A
		else:double=_B
		srp=self.reader.peek;chunks=[];start_mark=self.reader.get_mark();quote=srp();self.reader.forward();chunks.extend(self.scan_flow_scalar_non_spaces(double,start_mark))
		while srp()!=quote:chunks.extend(self.scan_flow_scalar_spaces(double,start_mark));chunks.extend(self.scan_flow_scalar_non_spaces(double,start_mark))
		self.reader.forward();end_mark=self.reader.get_mark();return ScalarToken(''.join(chunks),_B,start_mark,end_mark,style)
	ESCAPE_REPLACEMENTS={'0':_I,'a':'\x07','b':'\x08','t':'\t','\t':'\t','n':_E,'v':'\x0b','f':'\x0c','r':'\r','e':'\x1b',_D:_D,'"':'"','/':'/','\\':'\\','N':'\x85','_':'\xa0','L':'\u2028','P':'\u2029'};ESCAPE_CODES={'x':2,'u':4,'U':8}
	def scan_flow_scalar_non_spaces(self,double,start_mark):
		A='while scanning a double-quoted scalar';chunks=[];srp=self.reader.peek;srf=self.reader.forward
		while _A:
			length=0
			while srp(length)not in' \n\'"\\\x00\t\r\x85\u2028\u2029':length+=1
			if length!=0:chunks.append(self.reader.prefix(length));srf(length)
			ch=srp()
			if not double and ch=="'"and srp(1)=="'":chunks.append("'");srf(2)
			elif double and ch=="'"or not double and ch in'"\\':chunks.append(ch);srf()
			elif double and ch=='\\':
				srf();ch=srp()
				if ch in self.ESCAPE_REPLACEMENTS:chunks.append(self.ESCAPE_REPLACEMENTS[ch]);srf()
				elif ch in self.ESCAPE_CODES:
					length=self.ESCAPE_CODES[ch];srf()
					for k in range(length):
						if srp(k)not in _Y:raise ScannerError(A,start_mark,'expected escape sequence of %d hexdecimal numbers, but found %r'%(length,utf8(srp(k))),self.reader.get_mark())
					code=int(self.reader.prefix(length),16);chunks.append(unichr(code));srf(length)
				elif ch in'\n\r\x85\u2028\u2029':self.scan_line_break();chunks.extend(self.scan_flow_scalar_breaks(double,start_mark))
				else:raise ScannerError(A,start_mark,'found unknown escape character %r'%utf8(ch),self.reader.get_mark())
			else:return chunks
	def scan_flow_scalar_spaces(self,double,start_mark):
		srp=self.reader.peek;chunks=[];length=0
		while srp(length)in _K:length+=1
		whitespaces=self.reader.prefix(length);self.reader.forward(length);ch=srp()
		if ch==_I:raise ScannerError(_Z,start_mark,'found unexpected end of stream',self.reader.get_mark())
		elif ch in _P:
			line_break=self.scan_line_break();breaks=self.scan_flow_scalar_breaks(double,start_mark)
			if line_break!=_E:chunks.append(line_break)
			elif not breaks:chunks.append(_D)
			chunks.extend(breaks)
		else:chunks.append(whitespaces)
		return chunks
	def scan_flow_scalar_breaks(self,double,start_mark):
		chunks=[];srp=self.reader.peek;srf=self.reader.forward
		while _A:
			prefix=self.reader.prefix(3)
			if(prefix==_L or prefix==_M)and srp(3)in _THE_END_SPACE_TAB:raise ScannerError(_Z,start_mark,'found unexpected document separator',self.reader.get_mark())
			while srp()in _K:srf()
			if srp()in _P:chunks.append(self.scan_line_break())
			else:return chunks
	def scan_plain(self):
		srp=self.reader.peek;srf=self.reader.forward;chunks=[];start_mark=self.reader.get_mark();end_mark=start_mark;indent=self.indent+1;spaces=[]
		while _A:
			length=0
			if srp()==_F:break
			while _A:
				ch=srp(length)
				if ch==':'and srp(length+1)not in _THE_END_SPACE_TAB:0
				elif ch=='?'and self.scanner_processing_version!=(1,1):0
				elif ch in _THE_END_SPACE_TAB or not self.flow_level and ch==':'and srp(length+1)in _THE_END_SPACE_TAB or self.flow_level and ch in',:?[]{}':break
				length+=1
			if self.flow_level and ch==':'and srp(length+1)not in'\x00 \t\r\n\x85\u2028\u2029,[]{}':srf(length);raise ScannerError('while scanning a plain scalar',start_mark,"found unexpected ':'",self.reader.get_mark(),'Please check http://pyyaml.org/wiki/YAMLColonInFlowContext for details.')
			if length==0:break
			self.allow_simple_key=_B;chunks.extend(spaces);chunks.append(self.reader.prefix(length));srf(length);end_mark=self.reader.get_mark();spaces=self.scan_plain_spaces(indent,start_mark)
			if not spaces or srp()==_F or not self.flow_level and self.reader.column<indent:break
		token=ScalarToken(''.join(chunks),_A,start_mark,end_mark)
		if spaces and spaces[0]==_E:comment=CommentToken(''.join(spaces)+_E,start_mark,end_mark);token.add_post_comment(comment)
		return token
	def scan_plain_spaces(self,indent,start_mark):
		srp=self.reader.peek;srf=self.reader.forward;chunks=[];length=0
		while srp(length)in _D:length+=1
		whitespaces=self.reader.prefix(length);self.reader.forward(length);ch=srp()
		if ch in _P:
			line_break=self.scan_line_break();self.allow_simple_key=_A;prefix=self.reader.prefix(3)
			if(prefix==_L or prefix==_M)and srp(3)in _THE_END_SPACE_TAB:return
			breaks=[]
			while srp()in _X:
				if srp()==_D:srf()
				else:
					breaks.append(self.scan_line_break());prefix=self.reader.prefix(3)
					if(prefix==_L or prefix==_M)and srp(3)in _THE_END_SPACE_TAB:return
			if line_break!=_E:chunks.append(line_break)
			elif not breaks:chunks.append(_D)
			chunks.extend(breaks)
		elif whitespaces:chunks.append(whitespaces)
		return chunks
	def scan_tag_handle(self,name,start_mark):
		A="expected '!', but found %r";srp=self.reader.peek;ch=srp()
		if ch!=_H:raise ScannerError(_Q%(name,),start_mark,A%utf8(ch),self.reader.get_mark())
		length=1;ch=srp(length)
		if ch!=_D:
			while'0'<=ch<='9'or'A'<=ch<='Z'or'a'<=ch<='z'or ch in'-_':length+=1;ch=srp(length)
			if ch!=_H:self.reader.forward(length);raise ScannerError(_Q%(name,),start_mark,A%utf8(ch),self.reader.get_mark())
			length+=1
		value=self.reader.prefix(length);self.reader.forward(length);return value
	def scan_tag_uri(self,name,start_mark):
		srp=self.reader.peek;chunks=[];length=0;ch=srp(length)
		while'0'<=ch<='9'or'A'<=ch<='Z'or'a'<=ch<='z'or ch in"-;/?:@&=+$,_.!~*'()[]%"or self.scanner_processing_version>(1,1)and ch==_F:
			if ch=='%':chunks.append(self.reader.prefix(length));self.reader.forward(length);length=0;chunks.append(self.scan_uri_escapes(name,start_mark))
			else:length+=1
			ch=srp(length)
		if length!=0:chunks.append(self.reader.prefix(length));self.reader.forward(length);length=0
		if not chunks:raise ScannerError('while parsing a %s'%(name,),start_mark,'expected URI, but found %r'%utf8(ch),self.reader.get_mark())
		return''.join(chunks)
	def scan_uri_escapes(self,name,start_mark):
		A='utf-8';srp=self.reader.peek;srf=self.reader.forward;code_bytes=[];mark=self.reader.get_mark()
		while srp()=='%':
			srf()
			for k in range(2):
				if srp(k)not in _Y:raise ScannerError(_Q%(name,),start_mark,'expected URI escape sequence of 2 hexdecimal numbers, but found %r'%utf8(srp(k)),self.reader.get_mark())
			if PY3:code_bytes.append(int(self.reader.prefix(2),16))
			else:code_bytes.append(chr(int(self.reader.prefix(2),16)))
			srf(2)
		try:
			if PY3:value=bytes(code_bytes).decode(A)
			else:value=unicode(b''.join(code_bytes),A)
		except UnicodeDecodeError as exc:raise ScannerError(_Q%(name,),start_mark,str(exc),mark)
		return value
	def scan_line_break(self):
		ch=self.reader.peek()
		if ch in _a:
			if self.reader.prefix(2)=='\r\n':self.reader.forward(2)
			else:self.reader.forward()
			return _E
		elif ch in _b:self.reader.forward();return ch
		return''
class RoundTripScanner(Scanner):
	def check_token(self,*choices):
		while self.need_more_tokens():self.fetch_more_tokens()
		self._gather_comments()
		if bool(self.tokens):
			if not choices:return _A
			for choice in choices:
				if isinstance(self.tokens[0],choice):return _A
		return _B
	def peek_token(self):
		while self.need_more_tokens():self.fetch_more_tokens()
		self._gather_comments()
		if bool(self.tokens):return self.tokens[0]
	def _gather_comments(self):
		comments=[]
		if not self.tokens:return comments
		if isinstance(self.tokens[0],CommentToken):comment=self.tokens.pop(0);self.tokens_taken+=1;comments.append(comment)
		while self.need_more_tokens():
			self.fetch_more_tokens()
			if not self.tokens:return comments
			if isinstance(self.tokens[0],CommentToken):self.tokens_taken+=1;comment=self.tokens.pop(0);comments.append(comment)
		if len(comments)>=1:self.tokens[0].add_pre_comments(comments)
		if not self.done and len(self.tokens)<2:self.fetch_more_tokens()
	def get_token(self):
		while self.need_more_tokens():self.fetch_more_tokens()
		self._gather_comments()
		if bool(self.tokens):
			if len(self.tokens)>1 and isinstance(self.tokens[0],(ScalarToken,ValueToken,FlowSequenceEndToken,FlowMappingEndToken))and isinstance(self.tokens[1],CommentToken)and self.tokens[0].end_mark.line==self.tokens[1].start_mark.line:
				self.tokens_taken+=1;c=self.tokens.pop(1);self.fetch_more_tokens()
				while len(self.tokens)>1 and isinstance(self.tokens[1],CommentToken):self.tokens_taken+=1;c1=self.tokens.pop(1);c.value=c.value+_D*c1.start_mark.column+c1.value;self.fetch_more_tokens()
				self.tokens[0].add_post_comment(c)
			elif len(self.tokens)>1 and isinstance(self.tokens[0],ScalarToken)and isinstance(self.tokens[1],CommentToken)and self.tokens[0].end_mark.line!=self.tokens[1].start_mark.line:
				self.tokens_taken+=1;c=self.tokens.pop(1);c.value=_E*(c.start_mark.line-self.tokens[0].end_mark.line)+_D*c.start_mark.column+c.value;self.tokens[0].add_post_comment(c);self.fetch_more_tokens()
				while len(self.tokens)>1 and isinstance(self.tokens[1],CommentToken):self.tokens_taken+=1;c1=self.tokens.pop(1);c.value=c.value+_D*c1.start_mark.column+c1.value;self.fetch_more_tokens()
			self.tokens_taken+=1;return self.tokens.pop(0)
	def fetch_comment(self,comment):
		value,start_mark,end_mark=comment
		while value and value[-1]==_D:value=value[:-1]
		self.tokens.append(CommentToken(value,start_mark,end_mark))
	def scan_to_next_token(self):
		srp=self.reader.peek;srf=self.reader.forward
		if self.reader.index==0 and srp()==_U:srf()
		found=_B
		while not found:
			while srp()==_D:srf()
			ch=srp()
			if ch==_F:
				start_mark=self.reader.get_mark();comment=ch;srf()
				while ch not in _THE_END:
					ch=srp()
					if ch==_I:comment+=_E;break
					comment+=ch;srf()
				ch=self.scan_line_break()
				while len(ch)>0:comment+=ch;ch=self.scan_line_break()
				end_mark=self.reader.get_mark()
				if not self.flow_level:self.allow_simple_key=_A
				return comment,start_mark,end_mark
			if bool(self.scan_line_break()):
				start_mark=self.reader.get_mark()
				if not self.flow_level:self.allow_simple_key=_A
				ch=srp()
				if ch==_E:
					start_mark=self.reader.get_mark();comment=''
					while ch:ch=self.scan_line_break(empty_line=_A);comment+=ch
					if srp()==_F:comment=comment.rsplit(_E,1)[0]+_E
					end_mark=self.reader.get_mark();return comment,start_mark,end_mark
			else:found=_A
	def scan_line_break(self,empty_line=_B):
		ch=self.reader.peek()
		if ch in _a:
			if self.reader.prefix(2)=='\r\n':self.reader.forward(2)
			else:self.reader.forward()
			return _E
		elif ch in _b:self.reader.forward();return ch
		elif empty_line and ch in'\t ':self.reader.forward();return ch
		return''
	def scan_block_scalar(self,style,rt=_A):return Scanner.scan_block_scalar(self,style,rt=rt)
from __future__ import absolute_import
_C='\ufeff'
_B='ascii'
_A=None
import codecs
from.error import YAMLError,FileMark,StringMark,YAMLStreamError
from.compat import text_type,binary_type,PY3,UNICODE_SIZE
from.util import RegExp
if False:from typing import Any,Dict,Optional,List,Union,Text,Tuple,Optional
__all__=['Reader','ReaderError']
class ReaderError(YAMLError):
	def __init__(A,name,position,character,encoding,reason):A.name=name;A.character=character;A.position=position;A.encoding=encoding;A.reason=reason
	def __str__(A):
		if isinstance(A.character,binary_type):return'\'%s\' codec can\'t decode byte #x%02x: %s\n  in "%s", position %d'%(A.encoding,ord(A.character),A.reason,A.name,A.position)
		else:return'unacceptable character #x%04x: %s\n  in "%s", position %d'%(A.character,A.reason,A.name,A.position)
class Reader:
	def __init__(A,stream,loader=_A):
		A.loader=loader
		if A.loader is not _A and getattr(A.loader,'_reader',_A)is _A:A.loader._reader=A
		A.reset_reader();A.stream=stream
	def reset_reader(A):A.name=_A;A.stream_pointer=0;A.eof=True;A.buffer='';A.pointer=0;A.raw_buffer=_A;A.raw_decode=_A;A.encoding=_A;A.index=0;A.line=0;A.column=0
	@property
	def stream(self):
		try:return self._stream
		except AttributeError:raise YAMLStreamError('input stream needs to specified')
	@stream.setter
	def stream(self,val):
		B=val;A=self
		if B is _A:return
		A._stream=_A
		if isinstance(B,text_type):A.name='<unicode string>';A.check_printable(B);A.buffer=B+'\x00'
		elif isinstance(B,binary_type):A.name='<byte string>';A.raw_buffer=B;A.determine_encoding()
		else:
			if not hasattr(B,'read'):raise YAMLStreamError('stream argument needs to have a read() method')
			A._stream=B;A.name=getattr(A.stream,'name','<file>');A.eof=False;A.raw_buffer=_A;A.determine_encoding()
	def peek(A,index=0):
		B=index
		try:return A.buffer[A.pointer+B]
		except IndexError:A.update(B+1);return A.buffer[A.pointer+B]
	def prefix(A,length=1):
		B=length
		if A.pointer+B>=len(A.buffer):A.update(B)
		return A.buffer[A.pointer:A.pointer+B]
	def forward_1_1(A,length=1):
		B=length
		if A.pointer+B+1>=len(A.buffer):A.update(B+1)
		while B!=0:
			C=A.buffer[A.pointer];A.pointer+=1;A.index+=1
			if C in'\n\x85\u2028\u2029'or C=='\r'and A.buffer[A.pointer]!='\n':A.line+=1;A.column=0
			elif C!=_C:A.column+=1
			B-=1
	def forward(A,length=1):
		B=length
		if A.pointer+B+1>=len(A.buffer):A.update(B+1)
		while B!=0:
			C=A.buffer[A.pointer];A.pointer+=1;A.index+=1
			if C=='\n'or C=='\r'and A.buffer[A.pointer]!='\n':A.line+=1;A.column=0
			elif C!=_C:A.column+=1
			B-=1
	def get_mark(A):
		if A.stream is _A:return StringMark(A.name,A.index,A.line,A.column,A.buffer,A.pointer)
		else:return FileMark(A.name,A.index,A.line,A.column)
	def determine_encoding(A):
		while not A.eof and(A.raw_buffer is _A or len(A.raw_buffer)<2):A.update_raw()
		if isinstance(A.raw_buffer,binary_type):
			if A.raw_buffer.startswith(codecs.BOM_UTF16_LE):A.raw_decode=codecs.utf_16_le_decode;A.encoding='utf-16-le'
			elif A.raw_buffer.startswith(codecs.BOM_UTF16_BE):A.raw_decode=codecs.utf_16_be_decode;A.encoding='utf-16-be'
			else:A.raw_decode=codecs.utf_8_decode;A.encoding='utf-8'
		A.update(1)
	if UNICODE_SIZE==2:NON_PRINTABLE=RegExp('[^\t\n\r -~\x85\xa0-\ud7ff\ue000-�]')
	else:NON_PRINTABLE=RegExp('[^\t\n\r -~\x85\xa0-\ud7ff\ue000-�𐀀-\U0010ffff]')
	_printable_ascii=('\t\n\r'+''.join(map(chr,range(32,127)))).encode(_B)
	@classmethod
	def _get_non_printable_ascii(D,data):
		A=data.encode(_B);B=A.translate(_A,D._printable_ascii)
		if not B:return
		C=B[:1];return A.index(C),C.decode(_B)
	@classmethod
	def _get_non_printable_regex(B,data):
		A=B.NON_PRINTABLE.search(data)
		if not bool(A):return
		return A.start(),A.group()
	@classmethod
	def _get_non_printable(A,data):
		try:return A._get_non_printable_ascii(data)
		except UnicodeEncodeError:return A._get_non_printable_regex(data)
	def check_printable(A,data):
		B=A._get_non_printable(data)
		if B is not _A:C,D=B;E=A.index+(len(A.buffer)-A.pointer)+C;raise ReaderError(A.name,E,ord(D),'unicode','special characters are not allowed')
	def update(A,length):
		if A.raw_buffer is _A:return
		A.buffer=A.buffer[A.pointer:];A.pointer=0
		while len(A.buffer)<length:
			if not A.eof:A.update_raw()
			if A.raw_decode is not _A:
				try:C,E=A.raw_decode(A.raw_buffer,'strict',A.eof)
				except UnicodeDecodeError as B:
					if PY3:F=A.raw_buffer[B.start]
					else:F=B.object[B.start]
					if A.stream is not _A:D=A.stream_pointer-len(A.raw_buffer)+B.start
					elif A.stream is not _A:D=A.stream_pointer-len(A.raw_buffer)+B.start
					else:D=B.start
					raise ReaderError(A.name,D,F,B.encoding,B.reason)
			else:C=A.raw_buffer;E=len(C)
			A.check_printable(C);A.buffer+=C;A.raw_buffer=A.raw_buffer[E:]
			if A.eof:A.buffer+='\x00';A.raw_buffer=_A;break
	def update_raw(A,size=_A):
		C=size
		if C is _A:C=4096 if PY3 else 1024
		B=A.stream.read(C)
		if A.raw_buffer is _A:A.raw_buffer=B
		else:A.raw_buffer+=B
		A.stream_pointer+=len(B)
		if not B:A.eof=True
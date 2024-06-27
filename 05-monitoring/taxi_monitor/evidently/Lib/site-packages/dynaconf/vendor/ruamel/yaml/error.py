from __future__ import absolute_import
_E='  in "%s", line %d, column %d'
_D='column'
_C=False
_B='\n'
_A=None
import warnings,textwrap
from.compat import utf8
if _C:from typing import Any,Dict,Optional,List,Text
__all__=['FileMark','StringMark','CommentMark','YAMLError','MarkedYAMLError','ReusedAnchorWarning','UnsafeLoaderWarning','MarkedYAMLWarning','MarkedYAMLFutureWarning']
class StreamMark:
	__slots__='name','index','line',_D
	def __init__(A,name,index,line,column):A.name=name;A.index=index;A.line=line;A.column=column
	def __str__(A):B=_E%(A.name,A.line+1,A.column+1);return B
	def __eq__(A,other):
		B=other
		if A.line!=B.line or A.column!=B.column:return _C
		if A.name!=B.name or A.index!=B.index:return _C
		return True
	def __ne__(A,other):return not A.__eq__(other)
class FileMark(StreamMark):__slots__=()
class StringMark(StreamMark):
	__slots__='name','index','line',_D,'buffer','pointer'
	def __init__(A,name,index,line,column,buffer,pointer):StreamMark.__init__(A,name,index,line,column);A.buffer=buffer;A.pointer=pointer
	def get_snippet(A,indent=4,max_length=75):
		J=' ... ';I='\x00\r\n\x85\u2028\u2029';F=max_length;E=indent
		if A.buffer is _A:return
		D='';B=A.pointer
		while B>0 and A.buffer[B-1]not in I:
			B-=1
			if A.pointer-B>F/2-1:D=J;B+=5;break
		G='';C=A.pointer
		while C<len(A.buffer)and A.buffer[C]not in I:
			C+=1
			if C-A.pointer>F/2-1:G=J;C-=5;break
		K=utf8(A.buffer[B:C]);H='^';H='^ (line: {})'.format(A.line+1);return' '*E+D+K+G+_B+' '*(E+A.pointer-B+len(D))+H
	def __str__(A):
		B=A.get_snippet();C=_E%(A.name,A.line+1,A.column+1)
		if B is not _A:C+=':\n'+B
		return C
class CommentMark:
	__slots__=_D,
	def __init__(A,column):A.column=column
class YAMLError(Exception):0
class MarkedYAMLError(YAMLError):
	def __init__(A,context=_A,context_mark=_A,problem=_A,problem_mark=_A,note=_A,warn=_A):A.context=context;A.context_mark=context_mark;A.problem=problem;A.problem_mark=problem_mark;A.note=note
	def __str__(A):
		B=[]
		if A.context is not _A:B.append(A.context)
		if A.context_mark is not _A and(A.problem is _A or A.problem_mark is _A or A.context_mark.name!=A.problem_mark.name or A.context_mark.line!=A.problem_mark.line or A.context_mark.column!=A.problem_mark.column):B.append(str(A.context_mark))
		if A.problem is not _A:B.append(A.problem)
		if A.problem_mark is not _A:B.append(str(A.problem_mark))
		if A.note is not _A and A.note:C=textwrap.dedent(A.note);B.append(C)
		return _B.join(B)
class YAMLStreamError(Exception):0
class YAMLWarning(Warning):0
class MarkedYAMLWarning(YAMLWarning):
	def __init__(A,context=_A,context_mark=_A,problem=_A,problem_mark=_A,note=_A,warn=_A):A.context=context;A.context_mark=context_mark;A.problem=problem;A.problem_mark=problem_mark;A.note=note;A.warn=warn
	def __str__(A):
		B=[]
		if A.context is not _A:B.append(A.context)
		if A.context_mark is not _A and(A.problem is _A or A.problem_mark is _A or A.context_mark.name!=A.problem_mark.name or A.context_mark.line!=A.problem_mark.line or A.context_mark.column!=A.problem_mark.column):B.append(str(A.context_mark))
		if A.problem is not _A:B.append(A.problem)
		if A.problem_mark is not _A:B.append(str(A.problem_mark))
		if A.note is not _A and A.note:C=textwrap.dedent(A.note);B.append(C)
		if A.warn is not _A and A.warn:D=textwrap.dedent(A.warn);B.append(D)
		return _B.join(B)
class ReusedAnchorWarning(YAMLWarning):0
class UnsafeLoaderWarning(YAMLWarning):text="\nThe default 'Loader' for 'load(stream)' without further arguments can be unsafe.\nUse 'load(stream, Loader=ruamel.yaml.Loader)' explicitly if that is OK.\nAlternatively include the following in your code:\n\n  import warnings\n  warnings.simplefilter('ignore', ruamel.yaml.error.UnsafeLoaderWarning)\n\nIn most other cases you should consider using 'safe_load(stream)'"
warnings.simplefilter('once',UnsafeLoaderWarning)
class MantissaNoDotYAML1_1Warning(YAMLWarning):
	def __init__(A,node,flt_str):A.node=node;A.flt=flt_str
	def __str__(A):B=A.node.start_mark.line;C=A.node.start_mark.column;return'\nIn YAML 1.1 floating point values should have a dot (\'.\') in their mantissa.\nSee the Floating-Point Language-Independent Type for YAML™ Version 1.1 specification\n( http://yaml.org/type/float.html ). This dot is not required for JSON nor for YAML 1.2\n\nCorrect your float: "{}" on line: {}, column: {}\n\nor alternatively include the following in your code:\n\n  import warnings\n  warnings.simplefilter(\'ignore\', ruamel.yaml.error.MantissaNoDotYAML1_1Warning)\n\n'.format(A.flt,B,C)
warnings.simplefilter('once',MantissaNoDotYAML1_1Warning)
class YAMLFutureWarning(Warning):0
class MarkedYAMLFutureWarning(YAMLFutureWarning):
	def __init__(A,context=_A,context_mark=_A,problem=_A,problem_mark=_A,note=_A,warn=_A):A.context=context;A.context_mark=context_mark;A.problem=problem;A.problem_mark=problem_mark;A.note=note;A.warn=warn
	def __str__(A):
		B=[]
		if A.context is not _A:B.append(A.context)
		if A.context_mark is not _A and(A.problem is _A or A.problem_mark is _A or A.context_mark.name!=A.problem_mark.name or A.context_mark.line!=A.problem_mark.line or A.context_mark.column!=A.problem_mark.column):B.append(str(A.context_mark))
		if A.problem is not _A:B.append(A.problem)
		if A.problem_mark is not _A:B.append(str(A.problem_mark))
		if A.note is not _A and A.note:C=textwrap.dedent(A.note);B.append(C)
		if A.warn is not _A and A.warn:D=textwrap.dedent(A.warn);B.append(D)
		return _B.join(B)
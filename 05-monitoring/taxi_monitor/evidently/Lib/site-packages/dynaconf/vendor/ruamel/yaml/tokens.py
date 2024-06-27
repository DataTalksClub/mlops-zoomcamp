from __future__ import unicode_literals
_F=', line: '
_E='pre_done'
_D=False
_C='value'
_B='_comment'
_A=None
if _D:from typing import Text,Any,Dict,Optional,List;from.error import StreamMark
SHOWLINES=True
class Token:
	__slots__='start_mark','end_mark',_B
	def __init__(A,start_mark,end_mark):A.start_mark=start_mark;A.end_mark=end_mark
	def __repr__(A):
		C=[A for A in A.__slots__ if not A.endswith('_mark')];C.sort();B=', '.join(['%s=%r'%(B,getattr(A,B))for B in C])
		if SHOWLINES:
			try:B+=_F+str(A.start_mark.line)
			except:pass
		try:B+=', comment: '+str(A._comment)
		except:pass
		return'{}({})'.format(A.__class__.__name__,B)
	def add_post_comment(A,comment):
		if not hasattr(A,_B):A._comment=[_A,_A]
		A._comment[0]=comment
	def add_pre_comments(A,comments):
		if not hasattr(A,_B):A._comment=[_A,_A]
		assert A._comment[1]is _A;A._comment[1]=comments
	def get_comment(A):return getattr(A,_B,_A)
	@property
	def comment(self):return getattr(self,_B,_A)
	def move_comment(C,target,empty=_D):
		D=target;A=C.comment
		if A is _A:return
		if isinstance(D,(StreamEndToken,DocumentStartToken)):return
		delattr(C,_B);B=D.comment
		if not B:
			if empty:A=[A[0],A[1],_A,_A,A[0]]
			D._comment=A;return C
		if A[0]and B[0]or A[1]and B[1]:raise NotImplementedError('overlap in comment %r %r'%(A,B))
		if A[0]:B[0]=A[0]
		if A[1]:B[1]=A[1]
		return C
	def split_comment(B):
		A=B.comment
		if A is _A or A[0]is _A:return
		C=[A[0],_A]
		if A[1]is _A:delattr(B,_B)
		return C
class DirectiveToken(Token):
	__slots__='name',_C;id='<directive>'
	def __init__(A,name,value,start_mark,end_mark):Token.__init__(A,start_mark,end_mark);A.name=name;A.value=value
class DocumentStartToken(Token):__slots__=();id='<document start>'
class DocumentEndToken(Token):__slots__=();id='<document end>'
class StreamStartToken(Token):
	__slots__='encoding',;id='<stream start>'
	def __init__(A,start_mark=_A,end_mark=_A,encoding=_A):Token.__init__(A,start_mark,end_mark);A.encoding=encoding
class StreamEndToken(Token):__slots__=();id='<stream end>'
class BlockSequenceStartToken(Token):__slots__=();id='<block sequence start>'
class BlockMappingStartToken(Token):__slots__=();id='<block mapping start>'
class BlockEndToken(Token):__slots__=();id='<block end>'
class FlowSequenceStartToken(Token):__slots__=();id='['
class FlowMappingStartToken(Token):__slots__=();id='{'
class FlowSequenceEndToken(Token):__slots__=();id=']'
class FlowMappingEndToken(Token):__slots__=();id='}'
class KeyToken(Token):__slots__=();id='?'
class ValueToken(Token):__slots__=();id=':'
class BlockEntryToken(Token):__slots__=();id='-'
class FlowEntryToken(Token):__slots__=();id=','
class AliasToken(Token):
	__slots__=_C,;id='<alias>'
	def __init__(A,value,start_mark,end_mark):Token.__init__(A,start_mark,end_mark);A.value=value
class AnchorToken(Token):
	__slots__=_C,;id='<anchor>'
	def __init__(A,value,start_mark,end_mark):Token.__init__(A,start_mark,end_mark);A.value=value
class TagToken(Token):
	__slots__=_C,;id='<tag>'
	def __init__(A,value,start_mark,end_mark):Token.__init__(A,start_mark,end_mark);A.value=value
class ScalarToken(Token):
	__slots__=_C,'plain','style';id='<scalar>'
	def __init__(A,value,plain,start_mark,end_mark,style=_A):Token.__init__(A,start_mark,end_mark);A.value=value;A.plain=plain;A.style=style
class CommentToken(Token):
	__slots__=_C,_E;id='<comment>'
	def __init__(A,value,start_mark,end_mark):Token.__init__(A,start_mark,end_mark);A.value=value
	def reset(A):
		if hasattr(A,_E):delattr(A,_E)
	def __repr__(A):
		B='{!r}'.format(A.value)
		if SHOWLINES:
			try:B+=_F+str(A.start_mark.line);B+=', col: '+str(A.start_mark.column)
			except:pass
		return'CommentToken({})'.format(B)
	def __eq__(A,other):
		B=other
		if A.start_mark!=B.start_mark:return _D
		if A.end_mark!=B.end_mark:return _D
		if A.value!=B.value:return _D
		return True
	def __ne__(A,other):return not A.__eq__(other)
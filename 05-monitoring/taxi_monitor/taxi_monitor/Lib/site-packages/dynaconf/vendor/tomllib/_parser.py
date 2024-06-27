from __future__ import annotations
_H='flags'
_G='Cannot overwrite a value'
_F='recursive_flags'
_E='nested'
_D='\n'
_C=False
_B=None
_A=True
from collections.abc import Iterable
import string
from types import MappingProxyType
from typing import Any,BinaryIO,NamedTuple
from._re import RE_DATETIME,RE_LOCALTIME,RE_NUMBER,match_to_datetime,match_to_localtime,match_to_number
from._types import Key,ParseFloat,Pos
ASCII_CTRL=frozenset(chr(A)for A in range(32))|frozenset(chr(127))
ILLEGAL_BASIC_STR_CHARS=ASCII_CTRL-frozenset('\t')
ILLEGAL_MULTILINE_BASIC_STR_CHARS=ASCII_CTRL-frozenset('\t\n')
ILLEGAL_LITERAL_STR_CHARS=ILLEGAL_BASIC_STR_CHARS
ILLEGAL_MULTILINE_LITERAL_STR_CHARS=ILLEGAL_MULTILINE_BASIC_STR_CHARS
ILLEGAL_COMMENT_CHARS=ILLEGAL_BASIC_STR_CHARS
TOML_WS=frozenset(' \t')
TOML_WS_AND_NEWLINE=TOML_WS|frozenset(_D)
BARE_KEY_CHARS=frozenset(string.ascii_letters+string.digits+'-_')
KEY_INITIAL_CHARS=BARE_KEY_CHARS|frozenset('"\'')
HEXDIGIT_CHARS=frozenset(string.hexdigits)
BASIC_STR_ESCAPE_REPLACEMENTS=MappingProxyType({'\\b':'\x08','\\t':'\t','\\n':_D,'\\f':'\x0c','\\r':'\r','\\"':'"','\\\\':'\\'})
class TOMLDecodeError(ValueError):0
def load(A,*,parse_float=float):
	B=A.read()
	try:C=B.decode()
	except AttributeError:raise TypeError("File must be opened in binary mode, e.g. use `open('foo.toml', 'rb')`")from _B
	return loads(C,parse_float=parse_float)
def loads(H,*,parse_float=float):
	E=parse_float;B=H.replace('\r\n',_D);A=0;D=Output(NestedDict(),Flags());F=();E=make_safe_parse_float(E)
	while _A:
		A=skip_chars(B,A,TOML_WS)
		try:C=B[A]
		except IndexError:break
		if C==_D:A+=1;continue
		if C in KEY_INITIAL_CHARS:A=key_value_rule(B,A,D,F,E);A=skip_chars(B,A,TOML_WS)
		elif C=='[':
			try:G=B[A+1]
			except IndexError:G=_B
			D.flags.finalize_pending()
			if G=='[':A,F=create_list_rule(B,A,D)
			else:A,F=create_dict_rule(B,A,D)
			A=skip_chars(B,A,TOML_WS)
		elif C!='#':raise suffixed_err(B,A,'Invalid statement')
		A=skip_comment(B,A)
		try:C=B[A]
		except IndexError:break
		if C!=_D:raise suffixed_err(B,A,'Expected newline or end of document after a statement')
		A+=1
	return D.data.dict
class Flags:
	FROZEN=0;EXPLICIT_NEST=1
	def __init__(A):A._flags={};A._pending_flags=set()
	def add_pending(A,key,flag):A._pending_flags.add((key,flag))
	def finalize_pending(A):
		for(B,C)in A._pending_flags:A.set(B,C,recursive=_C)
		A._pending_flags.clear()
	def unset_all(C,key):
		A=C._flags
		for B in key[:-1]:
			if B not in A:return
			A=A[B][_E]
		A.pop(key[-1],_B)
	def set(D,key,flag,*,recursive):
		A=D._flags;E,B=key[:-1],key[-1]
		for C in E:
			if C not in A:A[C]={_H:set(),_F:set(),_E:{}}
			A=A[C][_E]
		if B not in A:A[B]={_H:set(),_F:set(),_E:{}}
		A[B][_F if recursive else _H].add(flag)
	def is_(G,key,flag):
		C=flag;B=key
		if not B:return _C
		A=G._flags
		for D in B[:-1]:
			if D not in A:return _C
			E=A[D]
			if C in E[_F]:return _A
			A=E[_E]
		F=B[-1]
		if F in A:A=A[F];return C in A[_H]or C in A[_F]
		return _C
class NestedDict:
	def __init__(A):A.dict={}
	def get_or_create_nest(C,key,*,access_lists=_A):
		A=C.dict
		for B in key:
			if B not in A:A[B]={}
			A=A[B]
			if access_lists and isinstance(A,list):A=A[-1]
			if not isinstance(A,dict):raise KeyError('There is no nest behind this key')
		return A
	def append_nest_to_list(D,key):
		A=D.get_or_create_nest(key[:-1]);B=key[-1]
		if B in A:
			C=A[B]
			if not isinstance(C,list):raise KeyError('An object other than list found behind this key')
			C.append({})
		else:A[B]=[{}]
class Output(NamedTuple):data:NestedDict;flags:Flags
def skip_chars(src,pos,chars):
	A=pos
	try:
		while src[A]in chars:A+=1
	except IndexError:pass
	return A
def skip_until(src,pos,expect,*,error_on,error_on_eof):
	E=error_on;D=expect;B=pos;A=src
	try:C=A.index(D,B)
	except ValueError:
		C=len(A)
		if error_on_eof:raise suffixed_err(A,C,f"Expected {D!r}")from _B
	if not E.isdisjoint(A[B:C]):
		while A[B]not in E:B+=1
		raise suffixed_err(A,B,f"Found invalid character {A[B]!r}")
	return C
def skip_comment(src,pos):
	A=pos
	try:B=src[A]
	except IndexError:B=_B
	if B=='#':return skip_until(src,A+1,_D,error_on=ILLEGAL_COMMENT_CHARS,error_on_eof=_C)
	return A
def skip_comments_and_array_ws(src,pos):
	A=pos
	while _A:
		B=A;A=skip_chars(src,A,TOML_WS_AND_NEWLINE);A=skip_comment(src,A)
		if A==B:return A
def create_dict_rule(src,pos,out):
	D=out;B=src;A=pos;A+=1;A=skip_chars(B,A,TOML_WS);A,C=parse_key(B,A)
	if D.flags.is_(C,Flags.EXPLICIT_NEST)or D.flags.is_(C,Flags.FROZEN):raise suffixed_err(B,A,f"Cannot declare {C} twice")
	D.flags.set(C,Flags.EXPLICIT_NEST,recursive=_C)
	try:D.data.get_or_create_nest(C)
	except KeyError:raise suffixed_err(B,A,_G)from _B
	if not B.startswith(']',A):raise suffixed_err(B,A,"Expected ']' at the end of a table declaration")
	return A+1,C
def create_list_rule(src,pos,out):
	D=out;B=src;A=pos;A+=2;A=skip_chars(B,A,TOML_WS);A,C=parse_key(B,A)
	if D.flags.is_(C,Flags.FROZEN):raise suffixed_err(B,A,f"Cannot mutate immutable namespace {C}")
	D.flags.unset_all(C);D.flags.set(C,Flags.EXPLICIT_NEST,recursive=_C)
	try:D.data.append_nest_to_list(C)
	except KeyError:raise suffixed_err(B,A,_G)from _B
	if not B.startswith(']]',A):raise suffixed_err(B,A,"Expected ']]' at the end of an array declaration")
	return A+2,C
def key_value_rule(src,pos,out,header,parse_float):
	E=header;C=out;B=src;A=pos;A,D,H=parse_key_value_pair(B,A,parse_float);K,I=D[:-1],D[-1];F=E+K;L=(E+D[:A]for A in range(1,len(D)))
	for G in L:
		if C.flags.is_(G,Flags.EXPLICIT_NEST):raise suffixed_err(B,A,f"Cannot redefine namespace {G}")
		C.flags.add_pending(G,Flags.EXPLICIT_NEST)
	if C.flags.is_(F,Flags.FROZEN):raise suffixed_err(B,A,f"Cannot mutate immutable namespace {F}")
	try:J=C.data.get_or_create_nest(F)
	except KeyError:raise suffixed_err(B,A,_G)from _B
	if I in J:raise suffixed_err(B,A,_G)
	if isinstance(H,(dict,list)):C.flags.set(E+D,Flags.FROZEN,recursive=_A)
	J[I]=H;return A
def parse_key_value_pair(src,pos,parse_float):
	B=src;A=pos;A,D=parse_key(B,A)
	try:C=B[A]
	except IndexError:C=_B
	if C!='=':raise suffixed_err(B,A,"Expected '=' after a key in a key/value pair")
	A+=1;A=skip_chars(B,A,TOML_WS);A,E=parse_value(B,A,parse_float);return A,D,E
def parse_key(src,pos):
	B=src;A=pos;A,C=parse_key_part(B,A);D=C,;A=skip_chars(B,A,TOML_WS)
	while _A:
		try:E=B[A]
		except IndexError:E=_B
		if E!='.':return A,D
		A+=1;A=skip_chars(B,A,TOML_WS);A,C=parse_key_part(B,A);D+=C,;A=skip_chars(B,A,TOML_WS)
def parse_key_part(src,pos):
	B=src;A=pos
	try:C=B[A]
	except IndexError:C=_B
	if C in BARE_KEY_CHARS:D=A;A=skip_chars(B,A,BARE_KEY_CHARS);return A,B[D:A]
	if C=="'":return parse_literal_str(B,A)
	if C=='"':return parse_one_line_basic_str(B,A)
	raise suffixed_err(B,A,'Invalid initial character for a key part')
def parse_one_line_basic_str(src,pos):pos+=1;return parse_basic_str(src,pos,multiline=_C)
def parse_array(src,pos,parse_float):
	B=src;A=pos;A+=1;C=[];A=skip_comments_and_array_ws(B,A)
	if B.startswith(']',A):return A+1,C
	while _A:
		A,E=parse_value(B,A,parse_float);C.append(E);A=skip_comments_and_array_ws(B,A);D=B[A:A+1]
		if D==']':return A+1,C
		if D!=',':raise suffixed_err(B,A,'Unclosed array')
		A+=1;A=skip_comments_and_array_ws(B,A)
		if B.startswith(']',A):return A+1,C
def parse_inline_table(src,pos,parse_float):
	B=src;A=pos;A+=1;D=NestedDict();F=Flags();A=skip_chars(B,A,TOML_WS)
	if B.startswith('}',A):return A+1,D.dict
	while _A:
		A,C,G=parse_key_value_pair(B,A,parse_float);J,E=C[:-1],C[-1]
		if F.is_(C,Flags.FROZEN):raise suffixed_err(B,A,f"Cannot mutate immutable namespace {C}")
		try:H=D.get_or_create_nest(J,access_lists=_C)
		except KeyError:raise suffixed_err(B,A,_G)from _B
		if E in H:raise suffixed_err(B,A,f"Duplicate inline table key {E!r}")
		H[E]=G;A=skip_chars(B,A,TOML_WS);I=B[A:A+1]
		if I=='}':return A+1,D.dict
		if I!=',':raise suffixed_err(B,A,'Unclosed inline table')
		if isinstance(G,(dict,list)):F.set(C,Flags.FROZEN,recursive=_A)
		A+=1;A=skip_chars(B,A,TOML_WS)
def parse_basic_str_escape(src,pos,*,multiline=_C):
	E="Unescaped '\\' in a string";D='\\\n';B=src;A=pos;C=B[A:A+2];A+=2
	if multiline and C in{'\\ ','\\\t',D}:
		if C!=D:
			A=skip_chars(B,A,TOML_WS)
			try:F=B[A]
			except IndexError:return A,''
			if F!=_D:raise suffixed_err(B,A,E)
			A+=1
		A=skip_chars(B,A,TOML_WS_AND_NEWLINE);return A,''
	if C=='\\u':return parse_hex_char(B,A,4)
	if C=='\\U':return parse_hex_char(B,A,8)
	try:return A,BASIC_STR_ESCAPE_REPLACEMENTS[C]
	except KeyError:raise suffixed_err(B,A,E)from _B
def parse_basic_str_escape_multiline(src,pos):return parse_basic_str_escape(src,pos,multiline=_A)
def parse_hex_char(src,pos,hex_len):
	C=hex_len;B=src;A=pos;D=B[A:A+C]
	if len(D)!=C or not HEXDIGIT_CHARS.issuperset(D):raise suffixed_err(B,A,'Invalid hex value')
	A+=C;E=int(D,16)
	if not is_unicode_scalar_value(E):raise suffixed_err(B,A,'Escaped character is not a Unicode scalar value')
	return A,chr(E)
def parse_literal_str(src,pos):A=pos;A+=1;B=A;A=skip_until(src,A,"'",error_on=ILLEGAL_LITERAL_STR_CHARS,error_on_eof=_A);return A+1,src[B:A]
def parse_multiline_str(src,pos,*,literal):
	B=src;A=pos;A+=3
	if B.startswith(_D,A):A+=1
	if literal:C="'";E=skip_until(B,A,"'''",error_on=ILLEGAL_MULTILINE_LITERAL_STR_CHARS,error_on_eof=_A);D=B[A:E];A=E+3
	else:C='"';A,D=parse_basic_str(B,A,multiline=_A)
	if not B.startswith(C,A):return A,D
	A+=1
	if not B.startswith(C,A):return A,D+C
	A+=1;return A,D+C*2
def parse_basic_str(src,pos,*,multiline):
	F=multiline;B=src;A=pos
	if F:G=ILLEGAL_MULTILINE_BASIC_STR_CHARS;H=parse_basic_str_escape_multiline
	else:G=ILLEGAL_BASIC_STR_CHARS;H=parse_basic_str_escape
	C='';D=A
	while _A:
		try:E=B[A]
		except IndexError:raise suffixed_err(B,A,'Unterminated string')from _B
		if E=='"':
			if not F:return A+1,C+B[D:A]
			if B.startswith('"""',A):return A+3,C+B[D:A]
			A+=1;continue
		if E=='\\':C+=B[D:A];A,I=H(B,A);C+=I;D=A;continue
		if E in G:raise suffixed_err(B,A,f"Illegal character {E!r}")
		A+=1
def parse_value(src,pos,parse_float):
	D=parse_float;B=src;A=pos
	try:C=B[A]
	except IndexError:C=_B
	if C=='"':
		if B.startswith('"""',A):return parse_multiline_str(B,A,literal=_C)
		return parse_one_line_basic_str(B,A)
	if C=="'":
		if B.startswith("'''",A):return parse_multiline_str(B,A,literal=_A)
		return parse_literal_str(B,A)
	if C=='t':
		if B.startswith('true',A):return A+4,_A
	if C=='f':
		if B.startswith('false',A):return A+5,_C
	if C=='[':return parse_array(B,A,D)
	if C=='{':return parse_inline_table(B,A,D)
	E=RE_DATETIME.match(B,A)
	if E:
		try:J=match_to_datetime(E)
		except ValueError as K:raise suffixed_err(B,A,'Invalid date or datetime')from K
		return E.end(),J
	F=RE_LOCALTIME.match(B,A)
	if F:return F.end(),match_to_localtime(F)
	G=RE_NUMBER.match(B,A)
	if G:return G.end(),match_to_number(G,D)
	H=B[A:A+3]
	if H in{'inf','nan'}:return A+3,D(H)
	I=B[A:A+4]
	if I in{'-inf','+inf','-nan','+nan'}:return A+4,D(I)
	raise suffixed_err(B,A,'Invalid value')
def suffixed_err(src,pos,msg):
	def A(src,pos):
		B=src;A=pos
		if A>=len(B):return'end of document'
		C=B.count(_D,0,A)+1
		if C==1:D=A+1
		else:D=A-B.rindex(_D,0,A)
		return f"line {C}, column {D}"
	return TOMLDecodeError(f"{msg} (at {A(src,pos)})")
def is_unicode_scalar_value(codepoint):A=codepoint;return 0<=A<=55295 or 57344<=A<=1114111
def make_safe_parse_float(parse_float):
	A=parse_float
	if A is float:return float
	def B(float_str):
		B=A(float_str)
		if isinstance(B,(dict,list)):raise ValueError('parse_float must not return dicts or lists')
		return B
	return B
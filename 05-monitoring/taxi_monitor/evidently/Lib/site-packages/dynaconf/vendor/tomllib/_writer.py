from __future__ import annotations
_C=True
_B=False
_A='\n'
from collections.abc import Generator,Mapping
from datetime import date,datetime,time
from decimal import Decimal
import string
from types import MappingProxyType
from typing import Any,BinaryIO,NamedTuple
ASCII_CTRL=frozenset(chr(A)for A in range(32))|frozenset(chr(127))
ILLEGAL_BASIC_STR_CHARS=frozenset('"\\')|ASCII_CTRL-frozenset('\t')
BARE_KEY_CHARS=frozenset(string.ascii_letters+string.digits+'-_')
ARRAY_TYPES=list,tuple
ARRAY_INDENT=' '*4
MAX_LINE_LENGTH=100
COMPACT_ESCAPES=MappingProxyType({'\x08':'\\b',_A:'\\n','\x0c':'\\f','\r':'\\r','"':'\\"','\\':'\\\\'})
def dump(__obj,__fp,*,multiline_strings=_B):
	A=Context(multiline_strings,{})
	for B in gen_table_chunks(__obj,A,name=''):__fp.write(B.encode())
def dumps(__obj,*,multiline_strings=_B):A=Context(multiline_strings,{});return''.join(gen_table_chunks(__obj,A,name=''))
class Context(NamedTuple):allow_multiline:bool;inline_table_cache:dict[(int,str)]
def gen_table_chunks(table,ctx,*,name,inside_aot=_B):
	H=inside_aot;G=ctx;C=name;D=_B;E=[];F=[]
	for(B,A)in table.items():
		if isinstance(A,dict):F.append((B,A,_B))
		elif is_aot(A)and not all(is_suitable_inline_table(A,G)for A in A):F.extend((B,A,_C)for A in A)
		else:E.append((B,A))
	if H or C and(E or not F):D=_C;yield f"[[{C}]]\n"if H else f"[{C}]\n"
	if E:
		D=_C
		for(B,A)in E:yield f"{format_key_part(B)} = {format_literal(A,G)}\n"
	for(B,A,J)in F:
		if D:yield _A
		else:D=_C
		I=format_key_part(B);K=f"{C}.{I}"if C else I;yield from gen_table_chunks(A,G,name=K,inside_aot=J)
def format_literal(obj,ctx,*,nest_level=0):
	B=ctx;A=obj
	if isinstance(A,bool):return'true'if A else'false'
	if isinstance(A,(int,float,date,datetime)):return str(A)
	if isinstance(A,Decimal):return format_decimal(A)
	if isinstance(A,time):
		if A.tzinfo:raise ValueError('TOML does not support offset times')
		return str(A)
	if isinstance(A,str):return format_string(A,allow_multiline=B.allow_multiline)
	if isinstance(A,ARRAY_TYPES):return format_inline_array(A,B,nest_level)
	if isinstance(A,dict):return format_inline_table(A,B)
	raise TypeError(f"Object of type {type(A)} is not TOML serializable")
def format_decimal(obj):
	C='-inf';B='inf';A=obj
	if A.is_nan():return'nan'
	if A==Decimal(B):return B
	if A==Decimal(C):return C
	return str(A)
def format_inline_table(obj,ctx):
	B=obj;A=ctx;C=id(B)
	if C in A.inline_table_cache:return A.inline_table_cache[C]
	if not B:D='{}'
	else:D='{ '+', '.join(f"{format_key_part(B)} = {format_literal(C,A)}"for(B,C)in B.items())+' }'
	A.inline_table_cache[C]=D;return D
def format_inline_array(obj,ctx,nest_level):
	A=nest_level
	if not obj:return'[]'
	B=ARRAY_INDENT*(1+A);C=ARRAY_INDENT*A;return'[\n'+',\n'.join(B+format_literal(C,ctx,nest_level=A+1)for C in obj)+f",\n{C}]"
def format_key_part(part):
	A=part
	if A and BARE_KEY_CHARS.issuperset(A):return A
	return format_string(A,allow_multiline=_B)
def format_string(s,*,allow_multiline):
	D=allow_multiline and _A in s
	if D:A='"""\n';s=s.replace('\r\n',_A)
	else:A='"'
	B=E=0
	while _C:
		try:C=s[B]
		except IndexError:
			A+=s[E:B]
			if D:return A+'"""'
			return A+'"'
		if C in ILLEGAL_BASIC_STR_CHARS:
			A+=s[E:B]
			if C in COMPACT_ESCAPES:
				if D and C==_A:A+=_A
				else:A+=COMPACT_ESCAPES[C]
			else:A+='\\u'+hex(ord(C))[2:].rjust(4,'0')
			E=B+1
		B+=1
def is_aot(obj):A=obj;return bool(isinstance(A,ARRAY_TYPES)and A and all(isinstance(A,dict)for A in A))
def is_suitable_inline_table(obj,ctx):A=f"{ARRAY_INDENT}{format_inline_table(obj,ctx)},";return len(A)<=MAX_LINE_LENGTH and _A not in A
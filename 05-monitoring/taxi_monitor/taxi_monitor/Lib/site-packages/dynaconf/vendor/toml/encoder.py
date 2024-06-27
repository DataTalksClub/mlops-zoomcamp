_C=' = '
_B=False
_A=None
import datetime,re,sys
from decimal import Decimal
from.decoder import InlineTableDict
if sys.version_info>=(3,):unicode=str
def dump(o,f,encoder=_A):
	if not f.write:raise TypeError('You can only dump an object to a file descriptor')
	A=dumps(o,encoder=encoder);f.write(A);return A
def dumps(o,encoder=_A):
	C=encoder;A=''
	if C is _A:C=TomlEncoder(o.__class__)
	B,D=C.dump_sections(o,'');A+=B;G=[id(o)]
	while D:
		H=[id(A)for A in D]
		for K in G:
			if K in H:raise ValueError('Circular reference detected')
		G+=H;I=C.get_empty_table()
		for E in D:
			B,F=C.dump_sections(D[E],E)
			if B or not B and not F:
				if A and A[-2:]!='\n\n':A+='\n'
				A+='['+E+']\n'
				if B:A+=B
			for J in F:I[E+'.'+J]=F[J]
		D=I
	return A
def _dump_str(v):
	D='\\';B='"'
	if sys.version_info<(3,)and hasattr(v,'decode')and isinstance(v,str):v=v.decode('utf-8')
	v='%r'%v
	if v[0]=='u':v=v[1:]
	E=v.startswith("'")
	if E or v.startswith(B):v=v[1:-1]
	if E:v=v.replace("\\'","'");v=v.replace(B,'\\"')
	v=v.split('\\x')
	while len(v)>1:
		A=-1
		if not v[0]:v=v[1:]
		v[0]=v[0].replace('\\\\',D);C=v[0][A]!=D
		while v[0][:A]and v[0][A]==D:C=not C;A-=1
		if C:F='x'
		else:F='u00'
		v=[v[0]+F+v[1]]+v[2:]
	return unicode(B+v[0]+B)
def _dump_float(v):return'{}'.format(v).replace('e+0','e+').replace('e-0','e-')
def _dump_time(v):
	A=v.utcoffset()
	if A is _A:return v.isoformat()
	return v.isoformat()[:-6]
class TomlEncoder:
	def __init__(A,_dict=dict,preserve=_B):A._dict=_dict;A.preserve=preserve;A.dump_funcs={str:_dump_str,unicode:_dump_str,list:A.dump_list,bool:lambda v:unicode(v).lower(),int:lambda v:v,float:_dump_float,Decimal:_dump_float,datetime.datetime:lambda v:v.isoformat().replace('+00:00','Z'),datetime.time:_dump_time,datetime.date:lambda v:v.isoformat()}
	def get_empty_table(A):return A._dict()
	def dump_list(B,v):
		A='['
		for C in v:A+=' '+unicode(B.dump_value(C))+','
		A+=']';return A
	def dump_inline_table(B,section):
		A=section;C=''
		if isinstance(A,dict):
			D=[]
			for(E,F)in A.items():G=B.dump_inline_table(F);D.append(E+_C+G)
			C+='{ '+', '.join(D)+' }\n';return C
		else:return unicode(B.dump_value(A))
	def dump_value(B,v):
		A=B.dump_funcs.get(type(v))
		if A is _A and hasattr(v,'__iter__'):A=B.dump_funcs[list]
		return A(v)if A is not _A else B.dump_funcs[str](v)
	def dump_sections(C,o,sup):
		D=sup;F=''
		if D!=''and D[-1]!='.':D+='.'
		M=C._dict();G=''
		for A in o:
			A=unicode(A);B=A
			if not re.match('^[A-Za-z0-9_-]+$',A):B=_dump_str(A)
			if not isinstance(o[A],dict):
				N=_B
				if isinstance(o[A],list):
					for L in o[A]:
						if isinstance(L,dict):N=True
				if N:
					for L in o[A]:
						H='\n';G+='[['+D+B+']]\n';I,J=C.dump_sections(L,D+B)
						if I:
							if I[0]=='[':H+=I
							else:G+=I
						while J:
							O=C._dict()
							for K in J:
								E,P=C.dump_sections(J[K],D+B+'.'+K)
								if E:H+='['+D+B+'.'+K+']\n';H+=E
								for E in P:O[K+'.'+E]=P[E]
							J=O
						G+=H
				elif o[A]is not _A:F+=B+_C+unicode(C.dump_value(o[A]))+'\n'
			elif C.preserve and isinstance(o[A],InlineTableDict):F+=B+_C+C.dump_inline_table(o[A])
			else:M[B]=o[A]
		F+=G;return F,M
class TomlPreserveInlineDictEncoder(TomlEncoder):
	def __init__(A,_dict=dict):super(TomlPreserveInlineDictEncoder,A).__init__(_dict,True)
class TomlArraySeparatorEncoder(TomlEncoder):
	def __init__(B,_dict=dict,preserve=_B,separator=','):
		A=separator;super(TomlArraySeparatorEncoder,B).__init__(_dict,preserve)
		if A.strip()=='':A=','+A
		elif A.strip(' \t\n\r,'):raise ValueError('Invalid separator for arrays')
		B.separator=A
	def dump_list(D,v):
		B=[];C='['
		for A in v:B.append(D.dump_value(A))
		while B!=[]:
			E=[]
			for A in B:
				if isinstance(A,list):
					for F in A:E.append(F)
				else:C+=' '+unicode(A)+D.separator
			B=E
		C+=']';return C
class TomlNumpyEncoder(TomlEncoder):
	def __init__(A,_dict=dict,preserve=_B):import numpy as B;super(TomlNumpyEncoder,A).__init__(_dict,preserve);A.dump_funcs[B.float16]=_dump_float;A.dump_funcs[B.float32]=_dump_float;A.dump_funcs[B.float64]=_dump_float;A.dump_funcs[B.int16]=A._dump_int;A.dump_funcs[B.int32]=A._dump_int;A.dump_funcs[B.int64]=A._dump_int
	def _dump_int(A,v):return'{}'.format(int(v))
class TomlPreserveCommentEncoder(TomlEncoder):
	def __init__(A,_dict=dict,preserve=_B):from dynaconf.vendor.toml.decoder import CommentValue as B;super(TomlPreserveCommentEncoder,A).__init__(_dict,preserve);A.dump_funcs[B]=lambda v:v.dump(A.dump_value)
class TomlPathlibEncoder(TomlEncoder):
	def _dump_pathlib_path(A,v):return _dump_str(str(v))
	def dump_value(A,v):
		if(3,4)<=sys.version_info:
			import pathlib as B
			if isinstance(v,B.PurePath):v=str(v)
		return super(TomlPathlibEncoder,A).dump_value(v)
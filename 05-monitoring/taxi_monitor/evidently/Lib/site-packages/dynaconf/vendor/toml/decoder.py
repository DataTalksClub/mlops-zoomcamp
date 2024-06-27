_Q='Reserved escape sequence used'
_P='false'
_O='true'
_N=','
_M=']'
_L=' '
_K='{'
_J='='
_I='['
_H='\\'
_G='\n'
_F=None
_E='.'
_D="'"
_C='"'
_B=True
_A=False
import datetime,io
from os import linesep
import re,sys
from.tz import TomlTz
if sys.version_info<(3,):_range=xrange
else:unicode=str;_range=range;basestring=str;unichr=chr
def _detect_pathlib_path(p):
	if(3,4)<=sys.version_info:
		import pathlib as A
		if isinstance(p,A.PurePath):return _B
	return _A
def _ispath(p):
	if isinstance(p,(bytes,basestring)):return _B
	return _detect_pathlib_path(p)
def _getpath(p):
	if(3,6)<=sys.version_info:import os;return os.fspath(p)
	if _detect_pathlib_path(p):return str(p)
	return p
try:FNFError=FileNotFoundError
except NameError:FNFError=IOError
TIME_RE=re.compile('([0-9]{2}):([0-9]{2}):([0-9]{2})(\\.([0-9]{3,6}))?')
class TomlDecodeError(ValueError):
	def __init__(A,msg,doc,pos):C=doc;B=pos;D=C.count(_G,0,B)+1;E=B-C.rfind(_G,0,B);F='{} (line {} column {} char {})'.format(msg,D,E,B);ValueError.__init__(A,F);A.msg=msg;A.doc=C;A.pos=B;A.lineno=D;A.colno=E
_number_with_underscores=re.compile('([0-9])(_([0-9]))*')
class CommentValue:
	def __init__(A,val,comment,beginline,_dict):A.val=val;B=_G if beginline else _L;A.comment=B+comment;A._dict=_dict
	def __getitem__(A,key):return A.val[key]
	def __setitem__(A,key,value):A.val[key]=value
	def dump(A,dump_value_func):
		B=dump_value_func(A.val)
		if isinstance(A.val,A._dict):return A.comment+_G+unicode(B)
		else:return unicode(B)+A.comment
def _strictly_valid_num(n):
	n=n.strip()
	if not n:return _A
	if n[0]=='_':return _A
	if n[-1]=='_':return _A
	if'_.'in n or'._'in n:return _A
	if len(n)==1:return _B
	if n[0]=='0'and n[1]not in[_E,'o','b','x']:return _A
	if n[0]=='+'or n[0]=='-':
		n=n[1:]
		if len(n)>1 and n[0]=='0'and n[1]!=_E:return _A
	if'__'in n:return _A
	return _B
def load(f,_dict=dict,decoder=_F):
	B=_dict;A=decoder
	if _ispath(f):
		with io.open(_getpath(f),encoding='utf-8')as G:return loads(G.read(),B,A)
	elif isinstance(f,list):
		from os import path as D;from warnings import warn
		if not[A for A in f if D.exists(A)]:C='Load expects a list to contain filenames only.';C+=linesep;C+='The list needs to contain the path of at least one existing file.';raise FNFError(C)
		if A is _F:A=TomlDecoder(B)
		E=A.get_empty_table()
		for F in f:
			if D.exists(F):E.update(load(F,B,A))
			else:warn('Non-existent filename in list with at least one valid filename')
		return E
	else:
		try:return loads(f.read(),B,A)
		except AttributeError:raise TypeError('You can only load a file descriptor, filename or list')
_groupname_re=re.compile('^[A-Za-z0-9_-]+$')
def loads(s,_dict=dict,decoder=_F):
	o="Invalid group name '";K=decoder;d=[]
	if K is _F:K=TomlDecoder(_dict)
	e=K.get_empty_table();G=e
	if not isinstance(s,basestring):raise TypeError('Expecting something like a string')
	if not isinstance(s,unicode):s=s.decode('utf8')
	I=s;B=list(s);b=0;J=_A;Q='';D=_A;L=_A;V=_B;U=_A;W=_A;O=0;c='';j='';k=1
	for(A,E)in enumerate(B):
		if E=='\r'and B[A+1]==_G:B[A]=_L;continue
		if O:
			c+=E
			if E==_G:raise TomlDecodeError('Key name found without value. Reached end of line.',I,A)
			if J:
				if E==Q:
					S=_A;F=1
					while A>=F and B[A-F]==_H:S=not S;F+=1
					if not S:O=2;J=_A;Q=''
				continue
			elif O==1:
				if E.isspace():O=2;continue
				elif E==_E:W=_B;continue
				elif E.isalnum()or E=='_'or E=='-':continue
				elif W and B[A-1]==_E and(E==_C or E==_D):J=_B;Q=E;continue
			elif O==2:
				if E.isspace():
					if W:
						X=B[A+1]
						if not X.isspace()and X!=_E:O=1
					continue
				if E==_E:
					W=_B;X=B[A+1]
					if not X.isspace()and X!=_E:O=1
					continue
			if E==_J:O=0;j=c[:-1].rstrip();c='';W=_A
			else:raise TomlDecodeError("Found invalid character in key name: '"+E+"'. Try quoting the key name.",I,A)
		if E==_D and Q!=_C:
			F=1
			try:
				while B[A-F]==_D:
					F+=1
					if F==3:break
			except IndexError:pass
			if F==3:D=not D;J=D
			else:J=not J
			if J:Q=_D
			else:Q=''
		if E==_C and Q!=_D:
			S=_A;F=1;f=_A
			try:
				while B[A-F]==_C:
					F+=1
					if F==3:f=_B;break
				if F==1 or F==3 and f:
					while B[A-F]==_H:S=not S;F+=1
			except IndexError:pass
			if not S:
				if f:D=not D;J=D
				else:J=not J
			if J:Q=_C
			else:Q=''
		if E=='#'and(not J and not U and not L):
			R=A;l=''
			try:
				while B[R]!=_G:l+=s[R];B[R]=_L;R+=1
			except IndexError:break
			if not b:K.preserve_comment(k,j,l,V)
		if E==_I and(not J and not U and not L):
			if V:
				if len(B)>A+1 and B[A+1]==_I:L=_B
				else:U=_B
			else:b+=1
		if E==_M and not J:
			if U:U=_A
			elif L:
				if B[A-1]==_M:L=_A
			else:b-=1
		if E==_G:
			if J or D:
				if not D:raise TomlDecodeError('Unbalanced quotes',I,A)
				if(B[A-1]==_D or B[A-1]==_C)and B[A-2]==B[A-1]:
					B[A]=B[A-1]
					if B[A-3]==B[A-1]:B[A-3]=_L
			elif b:B[A]=_L
			else:V=_B
			k+=1
		elif V and B[A]!=_L and B[A]!='\t':
			V=_A
			if not U and not L:
				if B[A]==_J:raise TomlDecodeError('Found empty keyname. ',I,A)
				O=1;c+=E
	if O:raise TomlDecodeError('Key name found without value. Reached end of file.',I,len(s))
	if J:raise TomlDecodeError('Unterminated string found. Reached end of file.',I,len(s))
	s=''.join(B);s=s.split(_G);T=_F;D='';P=_A;N=0
	for(g,C)in enumerate(s):
		if g>0:N+=len(s[g-1])+1
		K.embed_comments(g,G)
		if not D or P or _G not in D:C=C.strip()
		if C==''and(not T or P):continue
		if T:
			if P:D+=C
			else:D+=C
			P=_A;h=_A
			if D[0]==_I:h=C[-1]==_M
			elif len(C)>2:h=C[-1]==D[0]and C[-2]==D[0]and C[-3]==D[0]
			if h:
				try:p,r=K.load_value(D)
				except ValueError as Y:raise TomlDecodeError(str(Y),I,N)
				G[T]=p;T=_F;D=''
			else:
				F=len(D)-1
				while F>-1 and D[F]==_H:P=not P;F-=1
				if P:D=D[:-1]
				else:D+=_G
			continue
		if C[0]==_I:
			L=_A
			if len(C)==1:raise TomlDecodeError('Opening key group bracket on line by itself.',I,N)
			if C[1]==_I:L=_B;C=C[2:];Z=']]'
			else:C=C[1:];Z=_M
			A=1;q=K._get_split_on_quotes(C);i=_A
			for m in q:
				if not i and Z in m:break
				A+=m.count(Z);i=not i
			C=C.split(Z,A)
			if len(C)<A+1 or C[-1].strip()!='':raise TomlDecodeError('Key group not on a line by itself.',I,N)
			H=Z.join(C[:-1]).split(_E);A=0
			while A<len(H):
				H[A]=H[A].strip()
				if len(H[A])>0 and(H[A][0]==_C or H[A][0]==_D):
					a=H[A];R=A+1
					while not a[0]==a[-1]:
						R+=1
						if R>len(H)+2:raise TomlDecodeError(o+a+"' Something "+'went wrong.',I,N)
						a=_E.join(H[A:R]).strip()
					H[A]=a[1:-1];H[A+1:R]=[]
				elif not _groupname_re.match(H[A]):raise TomlDecodeError(o+H[A]+"'. Try quoting it.",I,N)
				A+=1
			G=e
			for A in _range(len(H)):
				M=H[A]
				if M=='':raise TomlDecodeError("Can't have a keygroup with an empty name",I,N)
				try:
					G[M]
					if A==len(H)-1:
						if M in d:
							d.remove(M)
							if L:raise TomlDecodeError("An implicitly defined table can't be an array",I,N)
						elif L:G[M].append(K.get_empty_table())
						else:raise TomlDecodeError('What? '+M+' already exists?'+str(G),I,N)
				except TypeError:
					G=G[-1]
					if M not in G:
						G[M]=K.get_empty_table()
						if A==len(H)-1 and L:G[M]=[K.get_empty_table()]
				except KeyError:
					if A!=len(H)-1:d.append(M)
					G[M]=K.get_empty_table()
					if A==len(H)-1 and L:G[M]=[K.get_empty_table()]
				G=G[M]
				if L:
					try:G=G[-1]
					except KeyError:pass
		elif C[0]==_K:
			if C[-1]!='}':raise TomlDecodeError('Line breaks are not allowed in inlineobjects',I,N)
			try:K.load_inline_object(C,G,T,P)
			except ValueError as Y:raise TomlDecodeError(str(Y),I,N)
		elif _J in C:
			try:n=K.load_line(C,G,T,P)
			except ValueError as Y:raise TomlDecodeError(str(Y),I,N)
			if n is not _F:T,D,P=n
	return e
def _load_date(val):
	A=val;G=0;F=_F
	try:
		if len(A)>19:
			if A[19]==_E:
				if A[-1].upper()=='Z':C=A[20:-1];D='Z'
				else:
					B=A[20:]
					if'+'in B:E=B.index('+');C=B[:E];D=B[E:]
					elif'-'in B:E=B.index('-');C=B[:E];D=B[E:]
					else:D=_F;C=B
				if D is not _F:F=TomlTz(D)
				G=int(int(C)*10**(6-len(C)))
			else:F=TomlTz(A[19:])
	except ValueError:F=_F
	if'-'not in A[1:]:return
	try:
		if len(A)==10:H=datetime.date(int(A[:4]),int(A[5:7]),int(A[8:10]))
		else:H=datetime.datetime(int(A[:4]),int(A[5:7]),int(A[8:10]),int(A[11:13]),int(A[14:16]),int(A[17:19]),G,F)
	except ValueError:return
	return H
def _load_unicode_escapes(v,hexbytes,prefix):
	G='Invalid escape sequence: ';E=prefix;C=_A;A=len(v)-1
	while A>-1 and v[A]==_H:C=not C;A-=1
	for D in hexbytes:
		if C:
			C=_A;A=len(D)-1
			while A>-1 and D[A]==_H:C=not C;A-=1
			v+=E;v+=D;continue
		B='';A=0;F=4
		if E=='\\U':F=8
		B=''.join(D[A:A+F]).lower()
		if B.strip('0123456789abcdef'):raise ValueError(G+B)
		if B[0]=='d'and B[1].strip('01234567'):raise ValueError(G+B+'. Only scalar unicode points are allowed.')
		v+=unichr(int(B,16));v+=unicode(D[len(B):])
	return v
_escapes=['0','b','f','n','r','t',_C]
_escapedchars=['\x00','\x08','\x0c',_G,'\r','\t',_C]
_escape_to_escapedchars=dict(zip(_escapes,_escapedchars))
def _unescape(v):
	A=0;B=_A
	while A<len(v):
		if B:
			B=_A
			if v[A]in _escapes:v=v[:A-1]+_escape_to_escapedchars[v[A]]+v[A+1:]
			elif v[A]==_H:v=v[:A-1]+v[A:]
			elif v[A]=='u'or v[A]=='U':A+=1
			else:raise ValueError(_Q)
			continue
		elif v[A]==_H:B=_B
		A+=1
	return v
class InlineTableDict:0
class TomlDecoder:
	def __init__(A,_dict=dict):A._dict=_dict
	def get_empty_table(A):return A._dict()
	def get_empty_inline_table(A):
		class B(A._dict,InlineTableDict):0
		return B()
	def load_inline_object(E,line,currentlevel,multikey=_A,multibackslash=_A):
		B=line[1:-1].split(_N);D=[]
		if len(B)==1 and not B[0].strip():B.pop()
		while len(B)>0:
			C=B.pop(0)
			try:H,A=C.split(_J,1)
			except ValueError:raise ValueError('Invalid inline table encountered')
			A=A.strip()
			if A[0]==A[-1]and A[0]in(_C,_D)or(A[0]in'-0123456789'or A in(_O,_P)or A[0]==_I and A[-1]==_M or A[0]==_K and A[-1]=='}'):D.append(C)
			elif len(B)>0:B[0]=C+_N+B[0]
			else:raise ValueError('Invalid inline table value encountered')
		for F in D:
			G=E.load_line(F,currentlevel,multikey,multibackslash)
			if G is not _F:break
	def _get_split_on_quotes(F,line):
		A=line.split(_C);D=_A;C=[]
		if len(A)>1 and _D in A[0]:
			B=A[0].split(_D);A=A[1:]
			while len(B)%2==0 and len(A):
				B[-1]+=_C+A[0];A=A[1:]
				if _D in B[-1]:B=B[:-1]+B[-1].split(_D)
			C+=B
		for E in A:
			if D:C.append(E)
			else:C+=E.split(_D);D=not D
		return C
	def load_line(E,line,currentlevel,multikey,multibackslash):
		P='Duplicate keys!';L=multikey;K=line;G=multibackslash;D=currentlevel;H=1;M=E._get_split_on_quotes(K);C=_A
		for F in M:
			if not C and _J in F:break
			H+=F.count(_J);C=not C
		A=K.split(_J,H);N=_strictly_valid_num(A[-1])
		if _number_with_underscores.match(A[-1]):A[-1]=A[-1].replace('_','')
		while len(A[-1])and(A[-1][0]!=_L and A[-1][0]!='\t'and A[-1][0]!=_D and A[-1][0]!=_C and A[-1][0]!=_I and A[-1][0]!=_K and A[-1].strip()!=_O and A[-1].strip()!=_P):
			try:float(A[-1]);break
			except ValueError:pass
			if _load_date(A[-1])is not _F:break
			if TIME_RE.match(A[-1]):break
			H+=1;Q=A[-1];A=K.split(_J,H)
			if Q==A[-1]:raise ValueError('Invalid date or number')
			if N:N=_strictly_valid_num(A[-1])
		A=[_J.join(A[:-1]).strip(),A[-1].strip()]
		if _E in A[0]:
			if _C in A[0]or _D in A[0]:
				M=E._get_split_on_quotes(A[0]);C=_A;B=[]
				for F in M:
					if C:B.append(F)
					else:B+=[A.strip()for A in F.split(_E)]
					C=not C
			else:B=A[0].split(_E)
			while B[-1]=='':B=B[:-1]
			for I in B[:-1]:
				if I=='':continue
				if I not in D:D[I]=E.get_empty_table()
				D=D[I]
			A[0]=B[-1].strip()
		elif(A[0][0]==_C or A[0][0]==_D)and A[0][-1]==A[0][0]:A[0]=_unescape(A[0][1:-1])
		J,R=E._load_line_multiline_str(A[1])
		if J>-1:
			while J>-1 and A[1][J+R]==_H:G=not G;J-=1
			if G:O=A[1][:-1]
			else:O=A[1]+_G
			L=A[0]
		else:S,T=E.load_value(A[1],N)
		try:D[A[0]];raise ValueError(P)
		except TypeError:raise ValueError(P)
		except KeyError:
			if L:return L,O,G
			else:D[A[0]]=S
	def _load_line_multiline_str(C,p):
		B=0
		if len(p)<3:return-1,B
		if p[0]==_I and(p.strip()[-1]!=_M and C._load_array_isstrarray(p)):
			A=p[1:].strip().split(_N)
			while len(A)>1 and A[-1][0]!=_C and A[-1][0]!=_D:A=A[:-2]+[A[-2]+_N+A[-1]]
			A=A[-1];B=len(p)-len(A);p=A
		if p[0]!=_C and p[0]!=_D:return-1,B
		if p[1]!=p[0]or p[2]!=p[0]:return-1,B
		if len(p)>5 and p[-1]==p[0]and p[-2]==p[0]and p[-3]==p[0]:return-1,B
		return len(p)-1,B
	def load_value(E,v,strictly_valid=_B):
		V='float';U='int';T='bool'
		if not v:raise ValueError('Empty value is invalid')
		if v==_O:return _B,T
		elif v==_P:return _A,T
		elif v[0]==_C or v[0]==_D:
			F=v[0];B=v[1:].split(F);G=_A;H=0
			if len(B)>1 and B[0]==''and B[1]=='':B=B[2:];G=_B
			I=_A
			for J in B:
				if J=='':
					if G:H+=1
					else:I=_B
				else:
					K=_A
					try:
						A=-1;N=J[A]
						while N==_H:K=not K;A-=1;N=J[A]
					except IndexError:pass
					if not K:
						if I:raise ValueError('Found tokens after a closed '+'string. Invalid TOML.')
						elif not G or H>1:I=_B
						else:H=0
			if F==_C:
				W=v.split(_H)[1:];C=_A
				for A in W:
					if A=='':C=not C
					else:
						if A[0]not in _escapes and(A[0]!='u'and A[0]!='U'and not C):raise ValueError(_Q)
						if C:C=_A
				for L in['\\u','\\U']:
					if L in v:O=v.split(L);v=_load_unicode_escapes(O[0],O[1:],L)
				v=_unescape(v)
			if len(v)>1 and v[1]==F and(len(v)<3 or v[1]==v[2]):v=v[2:-2]
			return v[1:-1],'str'
		elif v[0]==_I:return E.load_array(v),'array'
		elif v[0]==_K:P=E.get_empty_inline_table();E.load_inline_object(v,P);return P,'inline_object'
		elif TIME_RE.match(v):X,Y,Z,b,Q=TIME_RE.match(v).groups();a=datetime.time(int(X),int(Y),int(Z),int(Q)if Q else 0);return a,'time'
		else:
			R=_load_date(v)
			if R is not _F:return R,'date'
			if not strictly_valid:raise ValueError('Weirdness with leading zeroes or underscores in your number.')
			D=U;S=_A
			if v[0]=='-':S=_B;v=v[1:]
			elif v[0]=='+':v=v[1:]
			v=v.replace('_','');M=v.lower()
			if _E in v or'x'not in v and('e'in v or'E'in v):
				if _E in v and v.split(_E,1)[1]=='':raise ValueError('This float is missing digits after the point')
				if v[0]not in'0123456789':raise ValueError("This float doesn't have a leading digit")
				v=float(v);D=V
			elif len(M)==3 and(M=='inf'or M=='nan'):v=float(v);D=V
			if D==U:v=int(v,0)
			if S:return 0-v,D
			return v,D
	def bounded_string(C,s):
		if len(s)==0:return _B
		if s[-1]!=s[0]:return _A
		A=-2;B=_A
		while len(s)+A>0:
			if s[A]==_H:B=not B;A-=1
			else:break
		return not B
	def _load_array_isstrarray(A,a):
		a=a[1:-1].strip()
		if a!=''and(a[0]==_C or a[0]==_D):return _B
		return _A
	def load_array(H,a):
		I=_F;N=[];a=a.strip()
		if _I not in a[1:-1]or''!=a[1:-1].split(_I)[0].strip():
			Q=H._load_array_isstrarray(a)
			if not a[1:-1].strip().startswith(_K):a=a[1:-1].split(_N)
			else:
				O=[];E=1;A=2;J=1 if a[E]==_K else 0;F=_A
				while A<len(a[1:]):
					if a[A]==_C or a[A]==_D:
						if F:
							K=A-1
							while K>-1 and a[K]==_H:F=not F;K-=1
						F=not F
					if not F and a[A]==_K:J+=1
					if F or a[A]!='}':A+=1;continue
					elif a[A]=='}'and J>1:J-=1;A+=1;continue
					A+=1;O.append(a[E:A]);E=A+1
					while E<len(a[1:])and a[E]!=_K:E+=1
					A=E+1
				a=O
			B=0
			if Q:
				while B<len(a)-1:
					C=a[B].strip()
					while not H.bounded_string(C)or len(C)>2 and C[0]==C[1]==C[2]and C[-2]!=C[0]and C[-3]!=C[0]:
						a[B]=a[B]+_N+a[B+1];C=a[B].strip()
						if B<len(a)-2:a=a[:B+1]+a[B+2:]
						else:a=a[:B+1]
					B+=1
		else:
			G=list(a[1:-1]);a=[];L=0;M=0
			for D in _range(len(G)):
				if G[D]==_I:L+=1
				elif G[D]==_M:L-=1
				elif G[D]==_N and not L:a.append(''.join(G[M:D]));M=D+1
			a.append(''.join(G[M:]))
		for D in _range(len(a)):
			a[D]=a[D].strip()
			if a[D]!='':
				R,P=H.load_value(a[D])
				if I:
					if P!=I:raise ValueError('Not a homogeneous array')
				else:I=P
				N.append(R)
		return N
	def preserve_comment(A,line_no,key,comment,beginline):0
	def embed_comments(A,idx,currentlevel):0
class TomlPreserveCommentDecoder(TomlDecoder):
	def __init__(A,_dict=dict):A.saved_comments={};super(TomlPreserveCommentDecoder,A).__init__(_dict)
	def preserve_comment(A,line_no,key,comment,beginline):A.saved_comments[line_no]=key,comment,beginline
	def embed_comments(A,idx,currentlevel):
		B=currentlevel
		if idx not in A.saved_comments:return
		C,D,E=A.saved_comments[idx];B[C]=CommentValue(B[C],D,E,A._dict)
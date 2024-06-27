from __future__ import print_function
_D='RUAMELDEBUG'
_C=True
_B=False
_A=None
import sys,os,types,traceback
from abc import abstractmethod
if _B:from typing import Any,Dict,Optional,List,Union,BinaryIO,IO,Text,Tuple,Optional
_DEFAULT_YAML_VERSION=1,2
try:from ruamel.ordereddict import ordereddict
except:
	try:from collections import OrderedDict
	except ImportError:from ordereddict import OrderedDict
	class ordereddict(OrderedDict):
		if not hasattr(OrderedDict,'insert'):
			def insert(A,pos,key,value):
				C=value
				if pos>=len(A):A[key]=C;return
				B=ordereddict();B.update(A)
				for E in B:del A[E]
				for(F,D)in enumerate(B):
					if pos==F:A[key]=C
					A[D]=B[D]
PY2=sys.version_info[0]==2
PY3=sys.version_info[0]==3
if PY3:
	def utf8(s):return s
	def to_str(s):return s
	def to_unicode(s):return s
else:
	if _B:unicode=str
	def utf8(s):return s.encode('utf-8')
	def to_str(s):return str(s)
	def to_unicode(s):return unicode(s)
if PY3:string_types=str;integer_types=int;class_types=type;text_type=str;binary_type=bytes;MAXSIZE=sys.maxsize;unichr=chr;import io;StringIO=io.StringIO;BytesIO=io.BytesIO;no_limit_int=int;from collections.abc import Hashable,MutableSequence,MutableMapping,Mapping
else:string_types=basestring;integer_types=int,long;class_types=type,types.ClassType;text_type=unicode;binary_type=str;unichr=unichr;from StringIO import StringIO as _StringIO;StringIO=_StringIO;import cStringIO;BytesIO=cStringIO.StringIO;no_limit_int=long;from collections import Hashable,MutableSequence,MutableMapping,Mapping
if _B:StreamType=Any;StreamTextType=StreamType;VersionType=Union[(List[int],str,Tuple[(int,int)])]
if PY3:builtins_module='builtins'
else:builtins_module='__builtin__'
UNICODE_SIZE=4 if sys.maxunicode>65535 else 2
def with_metaclass(meta,*A):return meta('NewBase',A,{})
DBG_TOKEN=1
DBG_EVENT=2
DBG_NODE=4
_debug=_A
if _D in os.environ:
	_debugx=os.environ.get(_D)
	if _debugx is _A:_debug=0
	else:_debug=int(_debugx)
if bool(_debug):
	class ObjectCounter:
		def __init__(A):A.map={}
		def __call__(A,k):A.map[k]=A.map.get(k,0)+1
		def dump(A):
			for B in sorted(A.map):sys.stdout.write('{} -> {}'.format(B,A.map[B]))
	object_counter=ObjectCounter()
def dbg(val=_A):
	global _debug
	if _debug is _A:
		A=os.environ.get('YAMLDEBUG')
		if A is _A:_debug=0
		else:_debug=int(A)
	if val is _A:return _debug
	return _debug&val
class Nprint:
	def __init__(A,file_name=_A):A._max_print=_A;A._count=_A;A._file_name=file_name
	def __call__(A,*E,**F):
		if not bool(_debug):return
		B=sys.stdout if A._file_name is _A else open(A._file_name,'a');C=print;D=F.copy();D['file']=B;C(*E,**D);B.flush()
		if A._max_print is not _A:
			if A._count is _A:A._count=A._max_print
			A._count-=1
			if A._count==0:C('forced exit\n');traceback.print_stack();B.flush();sys.exit(0)
		if A._file_name:B.close()
	def set_max_print(A,i):A._max_print=i;A._count=_A
nprint=Nprint()
nprintf=Nprint('/var/tmp/ruamel.yaml.log')
def check_namespace_char(ch):
	A=ch
	if'!'<=A<='~':return _C
	if'\xa0'<=A<='\ud7ff':return _C
	if'\ue000'<=A<='�'and A!='\ufeff':return _C
	if'𐀀'<=A<='\U0010ffff':return _C
	return _B
def check_anchorname_char(ch):
	if ch in',[]{}':return _B
	return check_namespace_char(ch)
def version_tnf(t1,t2=_A):
	from dynaconf.vendor.ruamel.yaml import version_info as A
	if A<t1:return _C
	if t2 is not _A and A<t2:return
	return _B
class MutableSliceableSequence(MutableSequence):
	__slots__=()
	def __getitem__(A,index):
		B=index
		if not isinstance(B,slice):return A.__getsingleitem__(B)
		return type(A)([A[B]for B in range(*B.indices(len(A)))])
	def __setitem__(C,index,value):
		B=value;A=index
		if not isinstance(A,slice):return C.__setsingleitem__(A,B)
		assert iter(B)
		if A.step is _A:
			del C[A.start:A.stop]
			for F in reversed(B):C.insert(0 if A.start is _A else A.start,F)
		else:
			D=A.indices(len(C));E=(D[1]-D[0]-1)//D[2]+1
			if E<len(B):raise TypeError('too many elements in value {} < {}'.format(E,len(B)))
			elif E>len(B):raise TypeError('not enough elements in value {} > {}'.format(E,len(B)))
			for(G,H)in enumerate(range(*D)):C[H]=B[G]
	def __delitem__(A,index):
		B=index
		if not isinstance(B,slice):return A.__delsingleitem__(B)
		for C in reversed(range(*B.indices(len(A)))):del A[C]
	@abstractmethod
	def __getsingleitem__(self,index):raise IndexError
	@abstractmethod
	def __setsingleitem__(self,index,value):raise IndexError
	@abstractmethod
	def __delsingleitem__(self,index):raise IndexError
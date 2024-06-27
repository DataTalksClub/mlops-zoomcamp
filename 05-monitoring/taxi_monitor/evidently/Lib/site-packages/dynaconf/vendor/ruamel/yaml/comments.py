from __future__ import absolute_import,print_function
_E='CommentedMap'
_D=True
_C='\n'
_B=False
_A=None
import sys,copy
from.compat import ordereddict
from.compat import PY2,string_types,MutableSliceableSequence
from.scalarstring import ScalarString
from.anchor import Anchor
if PY2:from collections import MutableSet,Sized,Set,Mapping
else:from collections.abc import MutableSet,Sized,Set,Mapping
if _B:from typing import Any,Dict,Optional,List,Union,Optional,Iterator
__all__=['CommentedSeq','CommentedKeySeq',_E,'CommentedOrderedMap','CommentedSet','comment_attrib','merge_attrib']
comment_attrib='_yaml_comment'
format_attrib='_yaml_format'
line_col_attrib='_yaml_line_col'
merge_attrib='_yaml_merge'
tag_attrib='_yaml_tag'
class Comment:
	__slots__='comment','_items','_end','_start';attrib=comment_attrib
	def __init__(A):A.comment=_A;A._items={};A._end=[]
	def __str__(A):
		if bool(A._end):B=',\n  end='+str(A._end)
		else:B=''
		return'Comment(comment={0},\n  items={1}{2})'.format(A.comment,A._items,B)
	@property
	def items(self):return self._items
	@property
	def end(self):return self._end
	@end.setter
	def end(self,value):self._end=value
	@property
	def start(self):return self._start
	@start.setter
	def start(self,value):self._start=value
def NoComment():0
class Format:
	__slots__='_flow_style',;attrib=format_attrib
	def __init__(A):A._flow_style=_A
	def set_flow_style(A):A._flow_style=_D
	def set_block_style(A):A._flow_style=_B
	def flow_style(A,default=_A):
		if A._flow_style is _A:return default
		return A._flow_style
class LineCol:
	attrib=line_col_attrib
	def __init__(A):A.line=_A;A.col=_A;A.data=_A
	def add_kv_line_col(A,key,data):
		if A.data is _A:A.data={}
		A.data[key]=data
	def key(A,k):return A._kv(k,0,1)
	def value(A,k):return A._kv(k,2,3)
	def _kv(A,k,x0,x1):
		if A.data is _A:return
		B=A.data[k];return B[x0],B[x1]
	def item(A,idx):
		if A.data is _A:return
		return A.data[idx][0],A.data[idx][1]
	def add_idx_line_col(A,key,data):
		if A.data is _A:A.data={}
		A.data[key]=data
class Tag:
	__slots__='value',;attrib=tag_attrib
	def __init__(A):A.value=_A
	def __repr__(A):return'{0.__class__.__name__}({0.value!r})'.format(A)
class CommentedBase:
	@property
	def ca(self):
		A=self
		if not hasattr(A,Comment.attrib):setattr(A,Comment.attrib,Comment())
		return getattr(A,Comment.attrib)
	def yaml_end_comment_extend(A,comment,clear=_B):
		B=comment
		if B is _A:return
		if clear or A.ca.end is _A:A.ca.end=[]
		A.ca.end.extend(B)
	def yaml_key_comment_extend(C,key,comment,clear=_B):
		A=comment;B=C.ca._items.setdefault(key,[_A,_A,_A,_A])
		if clear or B[1]is _A:
			if A[1]is not _A:assert isinstance(A[1],list)
			B[1]=A[1]
		else:B[1].extend(A[0])
		B[0]=A[0]
	def yaml_value_comment_extend(C,key,comment,clear=_B):
		A=comment;B=C.ca._items.setdefault(key,[_A,_A,_A,_A])
		if clear or B[3]is _A:
			if A[1]is not _A:assert isinstance(A[1],list)
			B[3]=A[1]
		else:B[3].extend(A[0])
		B[2]=A[0]
	def yaml_set_start_comment(B,comment,indent=0):
		A=comment;from.error import CommentMark as C;from.tokens import CommentToken as D;E=B._yaml_get_pre_comment()
		if A[-1]==_C:A=A[:-1]
		F=C(indent)
		for G in A.split(_C):E.append(D('# '+G+_C,F,_A))
	def yaml_set_comment_before_after_key(J,key,before=_A,indent=0,after=_A,after_indent=_A):
		H=indent;E=after_indent;B=after;A=before;from dynaconf.vendor.ruamel.yaml.error import CommentMark as I;from dynaconf.vendor.ruamel.yaml.tokens import CommentToken as K
		def F(s,mark):return K(('# 'if s else'')+s+_C,mark,_A)
		if E is _A:E=H+2
		if A and len(A)>1 and A[-1]==_C:A=A[:-1]
		if B and B[-1]==_C:B=B[:-1]
		D=I(H);C=J.ca.items.setdefault(key,[_A,[],_A,_A])
		if A==_C:C[1].append(F('',D))
		elif A:
			for G in A.split(_C):C[1].append(F(G,D))
		if B:
			D=I(E)
			if C[3]is _A:C[3]=[]
			for G in B.split(_C):C[3].append(F(G,D))
	@property
	def fa(self):
		A=self
		if not hasattr(A,Format.attrib):setattr(A,Format.attrib,Format())
		return getattr(A,Format.attrib)
	def yaml_add_eol_comment(C,comment,key=NoComment,column=_A):
		B=column;A=comment;from.tokens import CommentToken as D;from.error import CommentMark as E
		if B is _A:
			try:B=C._yaml_get_column(key)
			except AttributeError:B=0
		if A[0]!='#':A='# '+A
		if B is _A:
			if A[0]=='#':A=' '+A;B=0
		F=E(B);G=[D(A,F,_A),_A];C._yaml_add_eol_comment(G,key=key)
	@property
	def lc(self):
		A=self
		if not hasattr(A,LineCol.attrib):setattr(A,LineCol.attrib,LineCol())
		return getattr(A,LineCol.attrib)
	def _yaml_set_line_col(A,line,col):A.lc.line=line;A.lc.col=col
	def _yaml_set_kv_line_col(A,key,data):A.lc.add_kv_line_col(key,data)
	def _yaml_set_idx_line_col(A,key,data):A.lc.add_idx_line_col(key,data)
	@property
	def anchor(self):
		A=self
		if not hasattr(A,Anchor.attrib):setattr(A,Anchor.attrib,Anchor())
		return getattr(A,Anchor.attrib)
	def yaml_anchor(A):
		if not hasattr(A,Anchor.attrib):return
		return A.anchor
	def yaml_set_anchor(A,value,always_dump=_B):A.anchor.value=value;A.anchor.always_dump=always_dump
	@property
	def tag(self):
		A=self
		if not hasattr(A,Tag.attrib):setattr(A,Tag.attrib,Tag())
		return getattr(A,Tag.attrib)
	def yaml_set_tag(A,value):A.tag.value=value
	def copy_attributes(B,t,memo=_A):
		for A in[Comment.attrib,Format.attrib,LineCol.attrib,Anchor.attrib,Tag.attrib,merge_attrib]:
			if hasattr(B,A):
				if memo is not _A:setattr(t,A,copy.deepcopy(getattr(B,A,memo)))
				else:setattr(t,A,getattr(B,A))
	def _yaml_add_eol_comment(A,comment,key):raise NotImplementedError
	def _yaml_get_pre_comment(A):raise NotImplementedError
	def _yaml_get_column(A,key):raise NotImplementedError
class CommentedSeq(MutableSliceableSequence,list,CommentedBase):
	__slots__=Comment.attrib,'_lst'
	def __init__(A,*B,**C):list.__init__(A,*B,**C)
	def __getsingleitem__(A,idx):return list.__getitem__(A,idx)
	def __setsingleitem__(B,idx,value):
		C=idx;A=value
		if C<len(B):
			if isinstance(A,string_types)and not isinstance(A,ScalarString)and isinstance(B[C],ScalarString):A=type(B[C])(A)
		list.__setitem__(B,C,A)
	def __delsingleitem__(A,idx=_A):
		B=idx;list.__delitem__(A,B);A.ca.items.pop(B,_A)
		for C in sorted(A.ca.items):
			if C<B:continue
			A.ca.items[C-1]=A.ca.items.pop(C)
	def __len__(A):return list.__len__(A)
	def insert(A,idx,val):
		list.insert(A,idx,val)
		for B in sorted(A.ca.items,reverse=_D):
			if B<idx:break
			A.ca.items[B+1]=A.ca.items.pop(B)
	def extend(A,val):list.extend(A,val)
	def __eq__(A,other):return list.__eq__(A,other)
	def _yaml_add_comment(A,comment,key=NoComment):
		B=comment
		if key is not NoComment:A.yaml_key_comment_extend(key,B)
		else:A.ca.comment=B
	def _yaml_add_eol_comment(A,comment,key):A._yaml_add_comment(comment,key=key)
	def _yaml_get_columnX(A,key):return A.ca.items[key][0].start_mark.column
	def _yaml_get_column(A,key):
		C=key;E=_A;B=_A;F,G=C-1,C+1
		if F in A.ca.items:B=F
		elif G in A.ca.items:B=G
		else:
			for(D,H)in enumerate(A):
				if D>=C:break
				if D not in A.ca.items:continue
				B=D
		if B is not _A:E=A._yaml_get_columnX(B)
		return E
	def _yaml_get_pre_comment(A):
		B=[]
		if A.ca.comment is _A:A.ca.comment=[_A,B]
		else:A.ca.comment[1]=B
		return B
	def __deepcopy__(A,memo):
		C=memo;B=A.__class__();C[id(A)]=B
		for D in A:B.append(copy.deepcopy(D,C));A.copy_attributes(B,memo=C)
		return B
	def __add__(A,other):return list.__add__(A,other)
	def sort(A,key=_A,reverse=_B):
		C=reverse
		if key is _A:B=sorted(zip(A,range(len(A))),reverse=C);list.__init__(A,[A[0]for A in B])
		else:B=sorted(zip(map(key,list.__iter__(A)),range(len(A))),reverse=C);list.__init__(A,[list.__getitem__(A,B[1])for B in B])
		D=A.ca.items;A.ca._items={}
		for(F,G)in enumerate(B):
			E=G[1]
			if E in D:A.ca.items[F]=D[E]
	def __repr__(A):return list.__repr__(A)
class CommentedKeySeq(tuple,CommentedBase):
	def _yaml_add_comment(A,comment,key=NoComment):
		B=comment
		if key is not NoComment:A.yaml_key_comment_extend(key,B)
		else:A.ca.comment=B
	def _yaml_add_eol_comment(A,comment,key):A._yaml_add_comment(comment,key=key)
	def _yaml_get_columnX(A,key):return A.ca.items[key][0].start_mark.column
	def _yaml_get_column(A,key):
		C=key;E=_A;B=_A;F,G=C-1,C+1
		if F in A.ca.items:B=F
		elif G in A.ca.items:B=G
		else:
			for(D,H)in enumerate(A):
				if D>=C:break
				if D not in A.ca.items:continue
				B=D
		if B is not _A:E=A._yaml_get_columnX(B)
		return E
	def _yaml_get_pre_comment(A):
		B=[]
		if A.ca.comment is _A:A.ca.comment=[_A,B]
		else:A.ca.comment[1]=B
		return B
class CommentedMapView(Sized):
	__slots__='_mapping',
	def __init__(A,mapping):A._mapping=mapping
	def __len__(A):B=len(A._mapping);return B
class CommentedMapKeysView(CommentedMapView,Set):
	__slots__=()
	@classmethod
	def _from_iterable(A,it):return set(it)
	def __contains__(A,key):return key in A._mapping
	def __iter__(A):
		for B in A._mapping:yield B
class CommentedMapItemsView(CommentedMapView,Set):
	__slots__=()
	@classmethod
	def _from_iterable(A,it):return set(it)
	def __contains__(A,item):
		B,C=item
		try:D=A._mapping[B]
		except KeyError:return _B
		else:return D==C
	def __iter__(A):
		for B in A._mapping._keys():yield(B,A._mapping[B])
class CommentedMapValuesView(CommentedMapView):
	__slots__=()
	def __contains__(A,value):
		for B in A._mapping:
			if value==A._mapping[B]:return _D
		return _B
	def __iter__(A):
		for B in A._mapping._keys():yield A._mapping[B]
class CommentedMap(ordereddict,CommentedBase):
	__slots__=Comment.attrib,'_ok','_ref'
	def __init__(A,*B,**C):A._ok=set();A._ref=[];ordereddict.__init__(A,*B,**C)
	def _yaml_add_comment(A,comment,key=NoComment,value=NoComment):
		C=value;B=comment
		if key is not NoComment:A.yaml_key_comment_extend(key,B);return
		if C is not NoComment:A.yaml_value_comment_extend(C,B)
		else:A.ca.comment=B
	def _yaml_add_eol_comment(A,comment,key):A._yaml_add_comment(comment,value=key)
	def _yaml_get_columnX(A,key):return A.ca.items[key][2].start_mark.column
	def _yaml_get_column(A,key):
		E=key;H=_A;B=_A;C,F,I=_A,_A,_A
		for D in A:
			if C is not _A and D!=E:F=D;break
			if D==E:C=I
			I=D
		if C in A.ca.items:B=C
		elif F in A.ca.items:B=F
		else:
			for G in A:
				if G>=E:break
				if G not in A.ca.items:continue
				B=G
		if B is not _A:H=A._yaml_get_columnX(B)
		return H
	def _yaml_get_pre_comment(A):
		B=[]
		if A.ca.comment is _A:A.ca.comment=[_A,B]
		else:A.ca.comment[1]=B
		return B
	def update(B,vals):
		A=vals
		try:ordereddict.update(B,A)
		except TypeError:
			for C in A:B[C]=A[C]
		try:B._ok.update(A.keys())
		except AttributeError:
			for C in A:B._ok.add(C[0])
	def insert(A,pos,key,value,comment=_A):
		C=comment;B=key;ordereddict.insert(A,pos,B,value);A._ok.add(B)
		if C is not _A:A.yaml_add_eol_comment(C,key=B)
	def mlget(C,key,default=_A,list_ok=_B):
		D=list_ok;B=default;A=key
		if not isinstance(A,list):return C.get(A,B)
		def E(key_list,level,d):
			B=level;A=key_list
			if not D:assert isinstance(d,dict)
			if B>=len(A):
				if B>len(A):raise IndexError
				return d[A[B-1]]
			return E(A,B+1,d[A[B-1]])
		try:return E(A,1,C)
		except KeyError:return B
		except(TypeError,IndexError):
			if not D:raise
			return B
	def __getitem__(B,key):
		A=key
		try:return ordereddict.__getitem__(B,A)
		except KeyError:
			for C in getattr(B,merge_attrib,[]):
				if A in C[1]:return C[1][A]
			raise
	def __setitem__(A,key,value):
		C=value;B=key
		if B in A:
			if isinstance(C,string_types)and not isinstance(C,ScalarString)and isinstance(A[B],ScalarString):C=type(A[B])(C)
		ordereddict.__setitem__(A,B,C);A._ok.add(B)
	def _unmerged_contains(A,key):
		if key in A._ok:return _D
	def __contains__(A,key):return bool(ordereddict.__contains__(A,key))
	def get(A,key,default=_A):
		try:return A.__getitem__(key)
		except:return default
	def __repr__(A):return ordereddict.__repr__(A).replace(_E,'ordereddict')
	def non_merged_items(A):
		for B in ordereddict.__iter__(A):
			if B in A._ok:yield(B,ordereddict.__getitem__(A,B))
	def __delitem__(A,key):
		B=key;A._ok.discard(B);ordereddict.__delitem__(A,B)
		for C in A._ref:C.update_key_value(B)
	def __iter__(A):
		for B in ordereddict.__iter__(A):yield B
	def _keys(A):
		for B in ordereddict.__iter__(A):yield B
	def __len__(A):return int(ordereddict.__len__(A))
	def __eq__(A,other):return bool(dict(A)==other)
	if PY2:
		def keys(A):return list(A._keys())
		def iterkeys(A):return A._keys()
		def viewkeys(A):return CommentedMapKeysView(A)
	else:
		def keys(A):return CommentedMapKeysView(A)
	if PY2:
		def _values(A):
			for B in ordereddict.__iter__(A):yield ordereddict.__getitem__(A,B)
		def values(A):return list(A._values())
		def itervalues(A):return A._values()
		def viewvalues(A):return CommentedMapValuesView(A)
	else:
		def values(A):return CommentedMapValuesView(A)
	def _items(A):
		for B in ordereddict.__iter__(A):yield(B,ordereddict.__getitem__(A,B))
	if PY2:
		def items(A):return list(A._items())
		def iteritems(A):return A._items()
		def viewitems(A):return CommentedMapItemsView(A)
	else:
		def items(A):return CommentedMapItemsView(A)
	@property
	def merge(self):
		A=self
		if not hasattr(A,merge_attrib):setattr(A,merge_attrib,[])
		return getattr(A,merge_attrib)
	def copy(A):
		B=type(A)()
		for(C,D)in A._items():B[C]=D
		A.copy_attributes(B);return B
	def add_referent(A,cm):
		if cm not in A._ref:A._ref.append(cm)
	def add_yaml_merge(A,value):
		C=value
		for B in C:
			B[1].add_referent(A)
			for(D,B)in B[1].items():
				if ordereddict.__contains__(A,D):continue
				ordereddict.__setitem__(A,D,B)
		A.merge.extend(C)
	def update_key_value(B,key):
		A=key
		if A in B._ok:return
		for C in B.merge:
			if A in C[1]:ordereddict.__setitem__(B,A,C[1][A]);return
		ordereddict.__delitem__(B,A)
	def __deepcopy__(A,memo):
		C=memo;B=A.__class__();C[id(A)]=B
		for D in A:B[D]=copy.deepcopy(A[D],C)
		A.copy_attributes(B,memo=C);return B
@classmethod
def raise_immutable(cls,*A,**B):raise TypeError('{} objects are immutable'.format(cls.__name__))
class CommentedKeyMap(CommentedBase,Mapping):
	__slots__=Comment.attrib,'_od'
	def __init__(A,*B,**C):
		if hasattr(A,'_od'):raise_immutable(A)
		try:A._od=ordereddict(*B,**C)
		except TypeError:
			if PY2:A._od=ordereddict(B[0].items())
			else:raise
	__delitem__=__setitem__=clear=pop=popitem=setdefault=update=raise_immutable
	def __getitem__(A,index):return A._od[index]
	def __iter__(A):
		for B in A._od.__iter__():yield B
	def __len__(A):return len(A._od)
	def __hash__(A):return hash(tuple(A.items()))
	def __repr__(A):
		if not hasattr(A,merge_attrib):return A._od.__repr__()
		return'ordereddict('+repr(list(A._od.items()))+')'
	@classmethod
	def fromkeys(A,v=_A):return CommentedKeyMap(dict.fromkeys(A,v))
	def _yaml_add_comment(A,comment,key=NoComment):
		B=comment
		if key is not NoComment:A.yaml_key_comment_extend(key,B)
		else:A.ca.comment=B
	def _yaml_add_eol_comment(A,comment,key):A._yaml_add_comment(comment,key=key)
	def _yaml_get_columnX(A,key):return A.ca.items[key][0].start_mark.column
	def _yaml_get_column(A,key):
		C=key;E=_A;B=_A;F,G=C-1,C+1
		if F in A.ca.items:B=F
		elif G in A.ca.items:B=G
		else:
			for(D,H)in enumerate(A):
				if D>=C:break
				if D not in A.ca.items:continue
				B=D
		if B is not _A:E=A._yaml_get_columnX(B)
		return E
	def _yaml_get_pre_comment(A):
		B=[]
		if A.ca.comment is _A:A.ca.comment=[_A,B]
		else:A.ca.comment[1]=B
		return B
class CommentedOrderedMap(CommentedMap):__slots__=Comment.attrib,
class CommentedSet(MutableSet,CommentedBase):
	__slots__=Comment.attrib,'odict'
	def __init__(A,values=_A):
		B=values;A.odict=ordereddict();MutableSet.__init__(A)
		if B is not _A:A|=B
	def _yaml_add_comment(A,comment,key=NoComment,value=NoComment):
		C=value;B=comment
		if key is not NoComment:A.yaml_key_comment_extend(key,B);return
		if C is not NoComment:A.yaml_value_comment_extend(C,B)
		else:A.ca.comment=B
	def _yaml_add_eol_comment(A,comment,key):A._yaml_add_comment(comment,value=key)
	def add(A,value):A.odict[value]=_A
	def discard(A,value):del A.odict[value]
	def __contains__(A,x):return x in A.odict
	def __iter__(A):
		for B in A.odict:yield B
	def __len__(A):return len(A.odict)
	def __repr__(A):return'set({0!r})'.format(A.odict.keys())
class TaggedScalar(CommentedBase):
	def __init__(A,value=_A,style=_A,tag=_A):
		A.value=value;A.style=style
		if tag is not _A:A.yaml_set_tag(tag)
	def __str__(A):return A.value
def dump_comments(d,name='',sep='.',out=sys.stdout):
	E='{}\n';D=out;C=sep;A=name
	if isinstance(d,dict)and hasattr(d,'ca'):
		if A:sys.stdout.write(E.format(A))
		D.write(E.format(d.ca))
		for B in d:dump_comments(d[B],name=A+C+B if A else B,sep=C,out=D)
	elif isinstance(d,list)and hasattr(d,'ca'):
		if A:sys.stdout.write(E.format(A))
		D.write(E.format(d.ca))
		for(F,B)in enumerate(d):dump_comments(B,name=A+C+str(F)if A else str(F),sep=C,out=D)
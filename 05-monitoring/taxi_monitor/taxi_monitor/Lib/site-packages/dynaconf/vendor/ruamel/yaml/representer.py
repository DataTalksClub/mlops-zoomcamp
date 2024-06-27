from __future__ import print_function,absolute_import,division
_T='tag:yaml.org,2002:'
_S='tag:yaml.org,2002:python/object:'
_R='__getstate__'
_Q='tag:yaml.org,2002:set'
_P='base64'
_O='tag:yaml.org,2002:python/object/new:'
_N='tag:yaml.org,2002:timestamp'
_M='tag:yaml.org,2002:map'
_L='tag:yaml.org,2002:seq'
_K='tag:yaml.org,2002:float'
_J='tag:yaml.org,2002:binary'
_I='tag:yaml.org,2002:null'
_H='%s.%s'
_G='tag:yaml.org,2002:int'
_F='comment'
_E='ascii'
_D='tag:yaml.org,2002:str'
_C=False
_B=True
_A=None
from.error import*
from.nodes import*
from.compat import text_type,binary_type,to_unicode,PY2,PY3
from.compat import ordereddict
from.compat import nprint,nprintf
from.scalarstring import LiteralScalarString,FoldedScalarString,SingleQuotedScalarString,DoubleQuotedScalarString,PlainScalarString
from.scalarint import ScalarInt,BinaryInt,OctalInt,HexInt,HexCapsInt
from.scalarfloat import ScalarFloat
from.scalarbool import ScalarBoolean
from.timestamp import TimeStamp
import datetime,sys,types
if PY3:import copyreg,base64
else:import copy_reg as copyreg
if _C:from typing import Dict,List,Any,Union,Text,Optional
__all__=['BaseRepresenter','SafeRepresenter','Representer','RepresenterError','RoundTripRepresenter']
class RepresenterError(YAMLError):0
if PY2:
	def get_classobj_bases(cls):
		bases=[cls]
		for base in cls.__bases__:bases.extend(get_classobj_bases(base))
		return bases
class BaseRepresenter:
	yaml_representers={};yaml_multi_representers={}
	def __init__(self,default_style=_A,default_flow_style=_A,dumper=_A):
		self.dumper=dumper
		if self.dumper is not _A:self.dumper._representer=self
		self.default_style=default_style;self.default_flow_style=default_flow_style;self.represented_objects={};self.object_keeper=[];self.alias_key=_A;self.sort_base_mapping_type_on_output=_B
	@property
	def serializer(self):
		try:
			if hasattr(self.dumper,'typ'):return self.dumper.serializer
			return self.dumper._serializer
		except AttributeError:return self
	def represent(self,data):node=self.represent_data(data);self.serializer.serialize(node);self.represented_objects={};self.object_keeper=[];self.alias_key=_A
	def represent_data(self,data):
		if self.ignore_aliases(data):self.alias_key=_A
		else:self.alias_key=id(data)
		if self.alias_key is not _A:
			if self.alias_key in self.represented_objects:node=self.represented_objects[self.alias_key];return node
			self.object_keeper.append(data)
		data_types=type(data).__mro__
		if PY2:
			if isinstance(data,types.InstanceType):data_types=get_classobj_bases(data.__class__)+list(data_types)
		if data_types[0]in self.yaml_representers:node=self.yaml_representers[data_types[0]](self,data)
		else:
			for data_type in data_types:
				if data_type in self.yaml_multi_representers:node=self.yaml_multi_representers[data_type](self,data);break
			else:
				if _A in self.yaml_multi_representers:node=self.yaml_multi_representers[_A](self,data)
				elif _A in self.yaml_representers:node=self.yaml_representers[_A](self,data)
				else:node=ScalarNode(_A,text_type(data))
		return node
	def represent_key(self,data):return self.represent_data(data)
	@classmethod
	def add_representer(cls,data_type,representer):
		if'yaml_representers'not in cls.__dict__:cls.yaml_representers=cls.yaml_representers.copy()
		cls.yaml_representers[data_type]=representer
	@classmethod
	def add_multi_representer(cls,data_type,representer):
		if'yaml_multi_representers'not in cls.__dict__:cls.yaml_multi_representers=cls.yaml_multi_representers.copy()
		cls.yaml_multi_representers[data_type]=representer
	def represent_scalar(self,tag,value,style=_A,anchor=_A):
		if style is _A:style=self.default_style
		comment=_A
		if style and style[0]in'|>':
			comment=getattr(value,_F,_A)
			if comment:comment=[_A,[comment]]
		node=ScalarNode(tag,value,style=style,comment=comment,anchor=anchor)
		if self.alias_key is not _A:self.represented_objects[self.alias_key]=node
		return node
	def represent_sequence(self,tag,sequence,flow_style=_A):
		value=[];node=SequenceNode(tag,value,flow_style=flow_style)
		if self.alias_key is not _A:self.represented_objects[self.alias_key]=node
		best_style=_B
		for item in sequence:
			node_item=self.represent_data(item)
			if not(isinstance(node_item,ScalarNode)and not node_item.style):best_style=_C
			value.append(node_item)
		if flow_style is _A:
			if self.default_flow_style is not _A:node.flow_style=self.default_flow_style
			else:node.flow_style=best_style
		return node
	def represent_omap(self,tag,omap,flow_style=_A):
		value=[];node=SequenceNode(tag,value,flow_style=flow_style)
		if self.alias_key is not _A:self.represented_objects[self.alias_key]=node
		best_style=_B
		for item_key in omap:item_val=omap[item_key];node_item=self.represent_data({item_key:item_val});value.append(node_item)
		if flow_style is _A:
			if self.default_flow_style is not _A:node.flow_style=self.default_flow_style
			else:node.flow_style=best_style
		return node
	def represent_mapping(self,tag,mapping,flow_style=_A):
		value=[];node=MappingNode(tag,value,flow_style=flow_style)
		if self.alias_key is not _A:self.represented_objects[self.alias_key]=node
		best_style=_B
		if hasattr(mapping,'items'):
			mapping=list(mapping.items())
			if self.sort_base_mapping_type_on_output:
				try:mapping=sorted(mapping)
				except TypeError:pass
		for(item_key,item_value)in mapping:
			node_key=self.represent_key(item_key);node_value=self.represent_data(item_value)
			if not(isinstance(node_key,ScalarNode)and not node_key.style):best_style=_C
			if not(isinstance(node_value,ScalarNode)and not node_value.style):best_style=_C
			value.append((node_key,node_value))
		if flow_style is _A:
			if self.default_flow_style is not _A:node.flow_style=self.default_flow_style
			else:node.flow_style=best_style
		return node
	def ignore_aliases(self,data):return _C
class SafeRepresenter(BaseRepresenter):
	def ignore_aliases(self,data):
		if data is _A or isinstance(data,tuple)and data==():return _B
		if isinstance(data,(binary_type,text_type,bool,int,float)):return _B
		return _C
	def represent_none(self,data):return self.represent_scalar(_I,'null')
	if PY3:
		def represent_str(self,data):return self.represent_scalar(_D,data)
		def represent_binary(self,data):
			if hasattr(base64,'encodebytes'):data=base64.encodebytes(data).decode(_E)
			else:data=base64.encodestring(data).decode(_E)
			return self.represent_scalar(_J,data,style='|')
	else:
		def represent_str(self,data):
			tag=_A;style=_A
			try:data=unicode(data,_E);tag=_D
			except UnicodeDecodeError:
				try:data=unicode(data,'utf-8');tag=_D
				except UnicodeDecodeError:data=data.encode(_P);tag=_J;style='|'
			return self.represent_scalar(tag,data,style=style)
		def represent_unicode(self,data):return self.represent_scalar(_D,data)
	def represent_bool(self,data,anchor=_A):
		try:value=self.dumper.boolean_representation[bool(data)]
		except AttributeError:
			if data:value='true'
			else:value='false'
		return self.represent_scalar('tag:yaml.org,2002:bool',value,anchor=anchor)
	def represent_int(self,data):return self.represent_scalar(_G,text_type(data))
	if PY2:
		def represent_long(self,data):return self.represent_scalar(_G,text_type(data))
	inf_value=1e300
	while repr(inf_value)!=repr(inf_value*inf_value):inf_value*=inf_value
	def represent_float(self,data):
		if data!=data or data==.0 and data==1.:value='.nan'
		elif data==self.inf_value:value='.inf'
		elif data==-self.inf_value:value='-.inf'
		else:
			value=to_unicode(repr(data)).lower()
			if getattr(self.serializer,'use_version',_A)==(1,1):
				if'.'not in value and'e'in value:value=value.replace('e','.0e',1)
		return self.represent_scalar(_K,value)
	def represent_list(self,data):return self.represent_sequence(_L,data)
	def represent_dict(self,data):return self.represent_mapping(_M,data)
	def represent_ordereddict(self,data):return self.represent_omap('tag:yaml.org,2002:omap',data)
	def represent_set(self,data):
		value={}
		for key in data:value[key]=_A
		return self.represent_mapping(_Q,value)
	def represent_date(self,data):value=to_unicode(data.isoformat());return self.represent_scalar(_N,value)
	def represent_datetime(self,data):value=to_unicode(data.isoformat(' '));return self.represent_scalar(_N,value)
	def represent_yaml_object(self,tag,data,cls,flow_style=_A):
		if hasattr(data,_R):state=data.__getstate__()
		else:state=data.__dict__.copy()
		return self.represent_mapping(tag,state,flow_style=flow_style)
	def represent_undefined(self,data):raise RepresenterError('cannot represent an object: %s'%(data,))
SafeRepresenter.add_representer(type(_A),SafeRepresenter.represent_none)
SafeRepresenter.add_representer(str,SafeRepresenter.represent_str)
if PY2:SafeRepresenter.add_representer(unicode,SafeRepresenter.represent_unicode)
else:SafeRepresenter.add_representer(bytes,SafeRepresenter.represent_binary)
SafeRepresenter.add_representer(bool,SafeRepresenter.represent_bool)
SafeRepresenter.add_representer(int,SafeRepresenter.represent_int)
if PY2:SafeRepresenter.add_representer(long,SafeRepresenter.represent_long)
SafeRepresenter.add_representer(float,SafeRepresenter.represent_float)
SafeRepresenter.add_representer(list,SafeRepresenter.represent_list)
SafeRepresenter.add_representer(tuple,SafeRepresenter.represent_list)
SafeRepresenter.add_representer(dict,SafeRepresenter.represent_dict)
SafeRepresenter.add_representer(set,SafeRepresenter.represent_set)
SafeRepresenter.add_representer(ordereddict,SafeRepresenter.represent_ordereddict)
if sys.version_info>=(2,7):import collections;SafeRepresenter.add_representer(collections.OrderedDict,SafeRepresenter.represent_ordereddict)
SafeRepresenter.add_representer(datetime.date,SafeRepresenter.represent_date)
SafeRepresenter.add_representer(datetime.datetime,SafeRepresenter.represent_datetime)
SafeRepresenter.add_representer(_A,SafeRepresenter.represent_undefined)
class Representer(SafeRepresenter):
	if PY2:
		def represent_str(self,data):
			tag=_A;style=_A
			try:data=unicode(data,_E);tag=_D
			except UnicodeDecodeError:
				try:data=unicode(data,'utf-8');tag='tag:yaml.org,2002:python/str'
				except UnicodeDecodeError:data=data.encode(_P);tag=_J;style='|'
			return self.represent_scalar(tag,data,style=style)
		def represent_unicode(self,data):
			tag=_A
			try:data.encode(_E);tag='tag:yaml.org,2002:python/unicode'
			except UnicodeEncodeError:tag=_D
			return self.represent_scalar(tag,data)
		def represent_long(self,data):
			tag=_G
			if int(data)is not data:tag='tag:yaml.org,2002:python/long'
			return self.represent_scalar(tag,to_unicode(data))
	def represent_complex(self,data):
		if data.imag==.0:data='%r'%data.real
		elif data.real==.0:data='%rj'%data.imag
		elif data.imag>0:data='%r+%rj'%(data.real,data.imag)
		else:data='%r%rj'%(data.real,data.imag)
		return self.represent_scalar('tag:yaml.org,2002:python/complex',data)
	def represent_tuple(self,data):return self.represent_sequence('tag:yaml.org,2002:python/tuple',data)
	def represent_name(self,data):
		try:name=_H%(data.__module__,data.__qualname__)
		except AttributeError:name=_H%(data.__module__,data.__name__)
		return self.represent_scalar('tag:yaml.org,2002:python/name:'+name,'')
	def represent_module(self,data):return self.represent_scalar('tag:yaml.org,2002:python/module:'+data.__name__,'')
	if PY2:
		def represent_instance(self,data):
			cls=data.__class__;class_name=_H%(cls.__module__,cls.__name__);args=_A;state=_A
			if hasattr(data,'__getinitargs__'):args=list(data.__getinitargs__())
			if hasattr(data,_R):state=data.__getstate__()
			else:state=data.__dict__
			if args is _A and isinstance(state,dict):return self.represent_mapping(_S+class_name,state)
			if isinstance(state,dict)and not state:return self.represent_sequence(_O+class_name,args)
			value={}
			if bool(args):value['args']=args
			value['state']=state;return self.represent_mapping(_O+class_name,value)
	def represent_object(self,data):
		cls=type(data)
		if cls in copyreg.dispatch_table:reduce=copyreg.dispatch_table[cls](data)
		elif hasattr(data,'__reduce_ex__'):reduce=data.__reduce_ex__(2)
		elif hasattr(data,'__reduce__'):reduce=data.__reduce__()
		else:raise RepresenterError('cannot represent object: %r'%(data,))
		reduce=(list(reduce)+[_A]*5)[:5];function,args,state,listitems,dictitems=reduce;args=list(args)
		if state is _A:state={}
		if listitems is not _A:listitems=list(listitems)
		if dictitems is not _A:dictitems=dict(dictitems)
		if function.__name__=='__newobj__':function=args[0];args=args[1:];tag=_O;newobj=_B
		else:tag='tag:yaml.org,2002:python/object/apply:';newobj=_C
		try:function_name=_H%(function.__module__,function.__qualname__)
		except AttributeError:function_name=_H%(function.__module__,function.__name__)
		if not args and not listitems and not dictitems and isinstance(state,dict)and newobj:return self.represent_mapping(_S+function_name,state)
		if not listitems and not dictitems and isinstance(state,dict)and not state:return self.represent_sequence(tag+function_name,args)
		value={}
		if args:value['args']=args
		if state or not isinstance(state,dict):value['state']=state
		if listitems:value['listitems']=listitems
		if dictitems:value['dictitems']=dictitems
		return self.represent_mapping(tag+function_name,value)
if PY2:Representer.add_representer(str,Representer.represent_str);Representer.add_representer(unicode,Representer.represent_unicode);Representer.add_representer(long,Representer.represent_long)
Representer.add_representer(complex,Representer.represent_complex)
Representer.add_representer(tuple,Representer.represent_tuple)
Representer.add_representer(type,Representer.represent_name)
if PY2:Representer.add_representer(types.ClassType,Representer.represent_name)
Representer.add_representer(types.FunctionType,Representer.represent_name)
Representer.add_representer(types.BuiltinFunctionType,Representer.represent_name)
Representer.add_representer(types.ModuleType,Representer.represent_module)
if PY2:Representer.add_multi_representer(types.InstanceType,Representer.represent_instance)
Representer.add_multi_representer(object,Representer.represent_object)
Representer.add_multi_representer(type,Representer.represent_name)
from.comments import CommentedMap,CommentedOrderedMap,CommentedSeq,CommentedKeySeq,CommentedKeyMap,CommentedSet,comment_attrib,merge_attrib,TaggedScalar
class RoundTripRepresenter(SafeRepresenter):
	def __init__(self,default_style=_A,default_flow_style=_A,dumper=_A):
		if not hasattr(dumper,'typ')and default_flow_style is _A:default_flow_style=_C
		SafeRepresenter.__init__(self,default_style=default_style,default_flow_style=default_flow_style,dumper=dumper)
	def ignore_aliases(self,data):
		try:
			if data.anchor is not _A and data.anchor.value is not _A:return _C
		except AttributeError:pass
		return SafeRepresenter.ignore_aliases(self,data)
	def represent_none(self,data):
		if len(self.represented_objects)==0 and not self.serializer.use_explicit_start:return self.represent_scalar(_I,'null')
		return self.represent_scalar(_I,'')
	def represent_literal_scalarstring(self,data):
		tag=_A;style='|';anchor=data.yaml_anchor(any=_B)
		if PY2 and not isinstance(data,unicode):data=unicode(data,_E)
		tag=_D;return self.represent_scalar(tag,data,style=style,anchor=anchor)
	represent_preserved_scalarstring=represent_literal_scalarstring
	def represent_folded_scalarstring(self,data):
		tag=_A;style='>';anchor=data.yaml_anchor(any=_B)
		for fold_pos in reversed(getattr(data,'fold_pos',[])):
			if data[fold_pos]==' 'and(fold_pos>0 and not data[fold_pos-1].isspace())and(fold_pos<len(data)and not data[fold_pos+1].isspace()):data=data[:fold_pos]+'\x07'+data[fold_pos:]
		if PY2 and not isinstance(data,unicode):data=unicode(data,_E)
		tag=_D;return self.represent_scalar(tag,data,style=style,anchor=anchor)
	def represent_single_quoted_scalarstring(self,data):
		tag=_A;style="'";anchor=data.yaml_anchor(any=_B)
		if PY2 and not isinstance(data,unicode):data=unicode(data,_E)
		tag=_D;return self.represent_scalar(tag,data,style=style,anchor=anchor)
	def represent_double_quoted_scalarstring(self,data):
		tag=_A;style='"';anchor=data.yaml_anchor(any=_B)
		if PY2 and not isinstance(data,unicode):data=unicode(data,_E)
		tag=_D;return self.represent_scalar(tag,data,style=style,anchor=anchor)
	def represent_plain_scalarstring(self,data):
		tag=_A;style='';anchor=data.yaml_anchor(any=_B)
		if PY2 and not isinstance(data,unicode):data=unicode(data,_E)
		tag=_D;return self.represent_scalar(tag,data,style=style,anchor=anchor)
	def insert_underscore(self,prefix,s,underscore,anchor=_A):
		A='_'
		if underscore is _A:return self.represent_scalar(_G,prefix+s,anchor=anchor)
		if underscore[0]:
			sl=list(s);pos=len(s)-underscore[0]
			while pos>0:sl.insert(pos,A);pos-=underscore[0]
			s=''.join(sl)
		if underscore[1]:s=A+s
		if underscore[2]:s+=A
		return self.represent_scalar(_G,prefix+s,anchor=anchor)
	def represent_scalar_int(self,data):
		if data._width is not _A:s='{:0{}d}'.format(data,data._width)
		else:s=format(data,'d')
		anchor=data.yaml_anchor(any=_B);return self.insert_underscore('',s,data._underscore,anchor=anchor)
	def represent_binary_int(self,data):
		if data._width is not _A:s='{:0{}b}'.format(data,data._width)
		else:s=format(data,'b')
		anchor=data.yaml_anchor(any=_B);return self.insert_underscore('0b',s,data._underscore,anchor=anchor)
	def represent_octal_int(self,data):
		if data._width is not _A:s='{:0{}o}'.format(data,data._width)
		else:s=format(data,'o')
		anchor=data.yaml_anchor(any=_B);return self.insert_underscore('0o',s,data._underscore,anchor=anchor)
	def represent_hex_int(self,data):
		if data._width is not _A:s='{:0{}x}'.format(data,data._width)
		else:s=format(data,'x')
		anchor=data.yaml_anchor(any=_B);return self.insert_underscore('0x',s,data._underscore,anchor=anchor)
	def represent_hex_caps_int(self,data):
		if data._width is not _A:s='{:0{}X}'.format(data,data._width)
		else:s=format(data,'X')
		anchor=data.yaml_anchor(any=_B);return self.insert_underscore('0x',s,data._underscore,anchor=anchor)
	def represent_scalar_float(self,data):
		B='{:{}0{}d}';A='0';value=_A;anchor=data.yaml_anchor(any=_B)
		if data!=data or data==.0 and data==1.:value='.nan'
		elif data==self.inf_value:value='.inf'
		elif data==-self.inf_value:value='-.inf'
		if value:return self.represent_scalar(_K,value,anchor=anchor)
		if data._exp is _A and data._prec>0 and data._prec==data._width-1:value='{}{:d}.'.format(data._m_sign if data._m_sign else'',abs(int(data)))
		elif data._exp is _A:
			prec=data._prec;ms=data._m_sign if data._m_sign else'';value='{}{:0{}.{}f}'.format(ms,abs(data),data._width-len(ms),data._width-prec-1)
			if prec==0 or prec==1 and ms!='':value=value.replace('0.','.')
			while len(value)<data._width:value+=A
		else:
			m,es='{:{}.{}e}'.format(data,data._width,data._width+(1 if data._m_sign else 0)).split('e');w=data._width if data._prec>0 else data._width+1
			if data<0:w+=1
			m=m[:w];e=int(es);m1,m2=m.split('.')
			while len(m1)+len(m2)<data._width-(1 if data._prec>=0 else 0):m2+=A
			if data._m_sign and data>0:m1='+'+m1
			esgn='+'if data._e_sign else''
			if data._prec<0:
				if m2!=A:e-=len(m2)
				else:m2=''
				while len(m1)+len(m2)-(1 if data._m_sign else 0)<data._width:m2+=A;e-=1
				value=m1+m2+data._exp+B.format(e,esgn,data._e_width)
			elif data._prec==0:e-=len(m2);value=m1+m2+'.'+data._exp+B.format(e,esgn,data._e_width)
			else:
				if data._m_lead0>0:m2=A*(data._m_lead0-1)+m1+m2;m1=A;m2=m2[:-data._m_lead0];e+=data._m_lead0
				while len(m1)<data._prec:m1+=m2[0];m2=m2[1:];e-=1
				value=m1+'.'+m2+data._exp+B.format(e,esgn,data._e_width)
		if value is _A:value=to_unicode(repr(data)).lower()
		return self.represent_scalar(_K,value,anchor=anchor)
	def represent_sequence(self,tag,sequence,flow_style=_A):
		value=[]
		try:flow_style=sequence.fa.flow_style(flow_style)
		except AttributeError:flow_style=flow_style
		try:anchor=sequence.yaml_anchor()
		except AttributeError:anchor=_A
		node=SequenceNode(tag,value,flow_style=flow_style,anchor=anchor)
		if self.alias_key is not _A:self.represented_objects[self.alias_key]=node
		best_style=_B
		try:
			comment=getattr(sequence,comment_attrib);node.comment=comment.comment
			if node.comment and node.comment[1]:
				for ct in node.comment[1]:ct.reset()
			item_comments=comment.items
			for v in item_comments.values():
				if v and v[1]:
					for ct in v[1]:ct.reset()
			item_comments=comment.items;node.comment=comment.comment
			try:node.comment.append(comment.end)
			except AttributeError:pass
		except AttributeError:item_comments={}
		for(idx,item)in enumerate(sequence):
			node_item=self.represent_data(item);self.merge_comments(node_item,item_comments.get(idx))
			if not(isinstance(node_item,ScalarNode)and not node_item.style):best_style=_C
			value.append(node_item)
		if flow_style is _A:
			if len(sequence)!=0 and self.default_flow_style is not _A:node.flow_style=self.default_flow_style
			else:node.flow_style=best_style
		return node
	def merge_comments(self,node,comments):
		if comments is _A:assert hasattr(node,_F);return node
		if getattr(node,_F,_A)is not _A:
			for(idx,val)in enumerate(comments):
				if idx>=len(node.comment):continue
				nc=node.comment[idx]
				if nc is not _A:assert val is _A or val==nc;comments[idx]=nc
		node.comment=comments;return node
	def represent_key(self,data):
		if isinstance(data,CommentedKeySeq):self.alias_key=_A;return self.represent_sequence(_L,data,flow_style=_B)
		if isinstance(data,CommentedKeyMap):self.alias_key=_A;return self.represent_mapping(_M,data,flow_style=_B)
		return SafeRepresenter.represent_key(self,data)
	def represent_mapping(self,tag,mapping,flow_style=_A):
		value=[]
		try:flow_style=mapping.fa.flow_style(flow_style)
		except AttributeError:flow_style=flow_style
		try:anchor=mapping.yaml_anchor()
		except AttributeError:anchor=_A
		node=MappingNode(tag,value,flow_style=flow_style,anchor=anchor)
		if self.alias_key is not _A:self.represented_objects[self.alias_key]=node
		best_style=_B
		try:
			comment=getattr(mapping,comment_attrib);node.comment=comment.comment
			if node.comment and node.comment[1]:
				for ct in node.comment[1]:ct.reset()
			item_comments=comment.items
			for v in item_comments.values():
				if v and v[1]:
					for ct in v[1]:ct.reset()
			try:node.comment.append(comment.end)
			except AttributeError:pass
		except AttributeError:item_comments={}
		merge_list=[m[1]for m in getattr(mapping,merge_attrib,[])]
		try:merge_pos=getattr(mapping,merge_attrib,[[0]])[0][0]
		except IndexError:merge_pos=0
		item_count=0
		if bool(merge_list):items=mapping.non_merged_items()
		else:items=mapping.items()
		for(item_key,item_value)in items:
			item_count+=1;node_key=self.represent_key(item_key);node_value=self.represent_data(item_value);item_comment=item_comments.get(item_key)
			if item_comment:
				assert getattr(node_key,_F,_A)is _A;node_key.comment=item_comment[:2];nvc=getattr(node_value,_F,_A)
				if nvc is not _A:nvc[0]=item_comment[2];nvc[1]=item_comment[3]
				else:node_value.comment=item_comment[2:]
			if not(isinstance(node_key,ScalarNode)and not node_key.style):best_style=_C
			if not(isinstance(node_value,ScalarNode)and not node_value.style):best_style=_C
			value.append((node_key,node_value))
		if flow_style is _A:
			if(item_count!=0 or bool(merge_list))and self.default_flow_style is not _A:node.flow_style=self.default_flow_style
			else:node.flow_style=best_style
		if bool(merge_list):
			if len(merge_list)==1:arg=self.represent_data(merge_list[0])
			else:arg=self.represent_data(merge_list);arg.flow_style=_B
			value.insert(merge_pos,(ScalarNode('tag:yaml.org,2002:merge','<<'),arg))
		return node
	def represent_omap(self,tag,omap,flow_style=_A):
		value=[]
		try:flow_style=omap.fa.flow_style(flow_style)
		except AttributeError:flow_style=flow_style
		try:anchor=omap.yaml_anchor()
		except AttributeError:anchor=_A
		node=SequenceNode(tag,value,flow_style=flow_style,anchor=anchor)
		if self.alias_key is not _A:self.represented_objects[self.alias_key]=node
		best_style=_B
		try:
			comment=getattr(omap,comment_attrib);node.comment=comment.comment
			if node.comment and node.comment[1]:
				for ct in node.comment[1]:ct.reset()
			item_comments=comment.items
			for v in item_comments.values():
				if v and v[1]:
					for ct in v[1]:ct.reset()
			try:node.comment.append(comment.end)
			except AttributeError:pass
		except AttributeError:item_comments={}
		for item_key in omap:
			item_val=omap[item_key];node_item=self.represent_data({item_key:item_val});item_comment=item_comments.get(item_key)
			if item_comment:
				if item_comment[1]:node_item.comment=[_A,item_comment[1]]
				assert getattr(node_item.value[0][0],_F,_A)is _A;node_item.value[0][0].comment=[item_comment[0],_A];nvc=getattr(node_item.value[0][1],_F,_A)
				if nvc is not _A:nvc[0]=item_comment[2];nvc[1]=item_comment[3]
				else:node_item.value[0][1].comment=item_comment[2:]
			value.append(node_item)
		if flow_style is _A:
			if self.default_flow_style is not _A:node.flow_style=self.default_flow_style
			else:node.flow_style=best_style
		return node
	def represent_set(self,setting):
		flow_style=_C;tag=_Q;value=[];flow_style=setting.fa.flow_style(flow_style)
		try:anchor=setting.yaml_anchor()
		except AttributeError:anchor=_A
		node=MappingNode(tag,value,flow_style=flow_style,anchor=anchor)
		if self.alias_key is not _A:self.represented_objects[self.alias_key]=node
		best_style=_B
		try:
			comment=getattr(setting,comment_attrib);node.comment=comment.comment
			if node.comment and node.comment[1]:
				for ct in node.comment[1]:ct.reset()
			item_comments=comment.items
			for v in item_comments.values():
				if v and v[1]:
					for ct in v[1]:ct.reset()
			try:node.comment.append(comment.end)
			except AttributeError:pass
		except AttributeError:item_comments={}
		for item_key in setting.odict:
			node_key=self.represent_key(item_key);node_value=self.represent_data(_A);item_comment=item_comments.get(item_key)
			if item_comment:assert getattr(node_key,_F,_A)is _A;node_key.comment=item_comment[:2]
			node_key.style=node_value.style='?'
			if not(isinstance(node_key,ScalarNode)and not node_key.style):best_style=_C
			if not(isinstance(node_value,ScalarNode)and not node_value.style):best_style=_C
			value.append((node_key,node_value))
		best_style=best_style;return node
	def represent_dict(self,data):
		try:t=data.tag.value
		except AttributeError:t=_A
		if t:
			if t.startswith('!!'):tag=_T+t[2:]
			else:tag=t
		else:tag=_M
		return self.represent_mapping(tag,data)
	def represent_list(self,data):
		try:t=data.tag.value
		except AttributeError:t=_A
		if t:
			if t.startswith('!!'):tag=_T+t[2:]
			else:tag=t
		else:tag=_L
		return self.represent_sequence(tag,data)
	def represent_datetime(self,data):
		A='delta';inter='T'if data._yaml['t']else' ';_yaml=data._yaml
		if _yaml[A]:data+=_yaml[A];value=data.isoformat(inter)
		else:value=data.isoformat(inter)
		if _yaml['tz']:value+=_yaml['tz']
		return self.represent_scalar(_N,to_unicode(value))
	def represent_tagged_scalar(self,data):
		try:tag=data.tag.value
		except AttributeError:tag=_A
		try:anchor=data.yaml_anchor()
		except AttributeError:anchor=_A
		return self.represent_scalar(tag,data.value,style=data.style,anchor=anchor)
	def represent_scalar_bool(self,data):
		try:anchor=data.yaml_anchor()
		except AttributeError:anchor=_A
		return SafeRepresenter.represent_bool(self,data,anchor=anchor)
RoundTripRepresenter.add_representer(type(_A),RoundTripRepresenter.represent_none)
RoundTripRepresenter.add_representer(LiteralScalarString,RoundTripRepresenter.represent_literal_scalarstring)
RoundTripRepresenter.add_representer(FoldedScalarString,RoundTripRepresenter.represent_folded_scalarstring)
RoundTripRepresenter.add_representer(SingleQuotedScalarString,RoundTripRepresenter.represent_single_quoted_scalarstring)
RoundTripRepresenter.add_representer(DoubleQuotedScalarString,RoundTripRepresenter.represent_double_quoted_scalarstring)
RoundTripRepresenter.add_representer(PlainScalarString,RoundTripRepresenter.represent_plain_scalarstring)
RoundTripRepresenter.add_representer(ScalarInt,RoundTripRepresenter.represent_scalar_int)
RoundTripRepresenter.add_representer(BinaryInt,RoundTripRepresenter.represent_binary_int)
RoundTripRepresenter.add_representer(OctalInt,RoundTripRepresenter.represent_octal_int)
RoundTripRepresenter.add_representer(HexInt,RoundTripRepresenter.represent_hex_int)
RoundTripRepresenter.add_representer(HexCapsInt,RoundTripRepresenter.represent_hex_caps_int)
RoundTripRepresenter.add_representer(ScalarFloat,RoundTripRepresenter.represent_scalar_float)
RoundTripRepresenter.add_representer(ScalarBoolean,RoundTripRepresenter.represent_scalar_bool)
RoundTripRepresenter.add_representer(CommentedSeq,RoundTripRepresenter.represent_list)
RoundTripRepresenter.add_representer(CommentedMap,RoundTripRepresenter.represent_dict)
RoundTripRepresenter.add_representer(CommentedOrderedMap,RoundTripRepresenter.represent_ordereddict)
if sys.version_info>=(2,7):import collections;RoundTripRepresenter.add_representer(collections.OrderedDict,RoundTripRepresenter.represent_ordereddict)
RoundTripRepresenter.add_representer(CommentedSet,RoundTripRepresenter.represent_set)
RoundTripRepresenter.add_representer(TaggedScalar,RoundTripRepresenter.represent_tagged_scalar)
RoundTripRepresenter.add_representer(TimeStamp,RoundTripRepresenter.represent_datetime)
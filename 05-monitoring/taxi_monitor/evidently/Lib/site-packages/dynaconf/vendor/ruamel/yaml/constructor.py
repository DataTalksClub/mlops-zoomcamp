from __future__ import print_function,absolute_import,division
_A5='expected the empty value, but found %r'
_A4='cannot find module %r (%s)'
_A3='expected non-empty name appended to the tag'
_A2='tag:yaml.org,2002:map'
_A1='tag:yaml.org,2002:seq'
_A0='tag:yaml.org,2002:set'
_z='tag:yaml.org,2002:pairs'
_y='tag:yaml.org,2002:omap'
_x='tag:yaml.org,2002:timestamp'
_w='tag:yaml.org,2002:binary'
_v='tag:yaml.org,2002:float'
_u='tag:yaml.org,2002:int'
_t='tag:yaml.org,2002:bool'
_s='tag:yaml.org,2002:null'
_r='could not determine a constructor for the tag %r'
_q='second'
_p='minute'
_o='failed to construct timestamp from "{}"'
_n='decodebytes'
_m='failed to convert base64 data into ascii: %s'
_l='expected a mapping or list of mappings for merging, but found %s'
_k='expected a mapping for merging, but found %s'
_j='                        Duplicate keys will become an error in future releases, and are errors\n                        by default when using the new API.\n                        '
_i='\n                        To suppress this check see:\n                           http://yaml.readthedocs.io/en/latest/api.html#duplicate-keys\n                        '
_h='tag:yaml.org,2002:merge'
_g='                    Duplicate keys will become an error in future releases, and are errors\n                    by default when using the new API.\n                    '
_f='\n                    To suppress this check see:\n                        http://yaml.readthedocs.io/en/latest/api.html#duplicate-keys\n                    '
_e='expected a sequence node, but found %s'
_d='expected a scalar node, but found %s'
_c='while constructing a Python module'
_b='expected a single mapping item, but found %d items'
_a='expected a mapping of length 1, but found %s'
_Z='expected a sequence, but found %s'
_Y='failed to decode base64 data: %s'
_X='tag:yaml.org,2002:value'
_W='found duplicate key "{}"'
_V='found unhashable key'
_U='found unacceptable key (%s)'
_T='__setstate__'
_S='tz_hour'
_R='hour'
_Q='ascii'
_P='tag:yaml.org,2002:str'
_O='utf-8'
_N='expected a mapping node, but found %s'
_M='tz_minute'
_L='+-'
_K='while constructing an ordered map'
_J='tz_sign'
_I='fraction'
_H='.'
_G=':'
_F='0'
_E='while constructing a mapping'
_D='_'
_C=True
_B=False
_A=None
import datetime,base64,binascii,re,sys,types,warnings
from.error import MarkedYAMLError,MarkedYAMLFutureWarning,MantissaNoDotYAML1_1Warning
from.nodes import*
from.nodes import SequenceNode,MappingNode,ScalarNode
from.compat import utf8,builtins_module,to_str,PY2,PY3,text_type,nprint,nprintf,version_tnf
from.compat import ordereddict,Hashable,MutableSequence
from.compat import MutableMapping
from.comments import*
from.comments import CommentedMap,CommentedOrderedMap,CommentedSet,CommentedKeySeq,CommentedSeq,TaggedScalar,CommentedKeyMap
from.scalarstring import SingleQuotedScalarString,DoubleQuotedScalarString,LiteralScalarString,FoldedScalarString,PlainScalarString,ScalarString
from.scalarint import ScalarInt,BinaryInt,OctalInt,HexInt,HexCapsInt
from.scalarfloat import ScalarFloat
from.scalarbool import ScalarBoolean
from.timestamp import TimeStamp
from.util import RegExp
if _B:from typing import Any,Dict,List,Set,Generator,Union,Optional
__all__=['BaseConstructor','SafeConstructor','Constructor','ConstructorError','RoundTripConstructor']
class ConstructorError(MarkedYAMLError):0
class DuplicateKeyFutureWarning(MarkedYAMLFutureWarning):0
class DuplicateKeyError(MarkedYAMLFutureWarning):0
class BaseConstructor:
	yaml_constructors={};yaml_multi_constructors={}
	def __init__(self,preserve_quotes=_A,loader=_A):
		self.loader=loader
		if self.loader is not _A and getattr(self.loader,'_constructor',_A)is _A:self.loader._constructor=self
		self.loader=loader;self.yaml_base_dict_type=dict;self.yaml_base_list_type=list;self.constructed_objects={};self.recursive_objects={};self.state_generators=[];self.deep_construct=_B;self._preserve_quotes=preserve_quotes;self.allow_duplicate_keys=version_tnf((0,15,1),(0,16))
	@property
	def composer(self):
		if hasattr(self.loader,'typ'):return self.loader.composer
		try:return self.loader._composer
		except AttributeError:sys.stdout.write('slt {}\n'.format(type(self)));sys.stdout.write('slc {}\n'.format(self.loader._composer));sys.stdout.write('{}\n'.format(dir(self)));raise
	@property
	def resolver(self):
		if hasattr(self.loader,'typ'):return self.loader.resolver
		return self.loader._resolver
	def check_data(self):return self.composer.check_node()
	def get_data(self):
		if self.composer.check_node():return self.construct_document(self.composer.get_node())
	def get_single_data(self):
		node=self.composer.get_single_node()
		if node is not _A:return self.construct_document(node)
	def construct_document(self,node):
		data=self.construct_object(node)
		while bool(self.state_generators):
			state_generators=self.state_generators;self.state_generators=[]
			for generator in state_generators:
				for _dummy in generator:0
		self.constructed_objects={};self.recursive_objects={};self.deep_construct=_B;return data
	def construct_object(self,node,deep=_B):
		if node in self.constructed_objects:return self.constructed_objects[node]
		if deep:old_deep=self.deep_construct;self.deep_construct=_C
		if node in self.recursive_objects:return self.recursive_objects[node]
		self.recursive_objects[node]=_A;data=self.construct_non_recursive_object(node);self.constructed_objects[node]=data;del self.recursive_objects[node]
		if deep:self.deep_construct=old_deep
		return data
	def construct_non_recursive_object(self,node,tag=_A):
		constructor=_A;tag_suffix=_A
		if tag is _A:tag=node.tag
		if tag in self.yaml_constructors:constructor=self.yaml_constructors[tag]
		else:
			for tag_prefix in self.yaml_multi_constructors:
				if tag.startswith(tag_prefix):tag_suffix=tag[len(tag_prefix):];constructor=self.yaml_multi_constructors[tag_prefix];break
			else:
				if _A in self.yaml_multi_constructors:tag_suffix=tag;constructor=self.yaml_multi_constructors[_A]
				elif _A in self.yaml_constructors:constructor=self.yaml_constructors[_A]
				elif isinstance(node,ScalarNode):constructor=self.__class__.construct_scalar
				elif isinstance(node,SequenceNode):constructor=self.__class__.construct_sequence
				elif isinstance(node,MappingNode):constructor=self.__class__.construct_mapping
		if tag_suffix is _A:data=constructor(self,node)
		else:data=constructor(self,tag_suffix,node)
		if isinstance(data,types.GeneratorType):
			generator=data;data=next(generator)
			if self.deep_construct:
				for _dummy in generator:0
			else:self.state_generators.append(generator)
		return data
	def construct_scalar(self,node):
		if not isinstance(node,ScalarNode):raise ConstructorError(_A,_A,_d%node.id,node.start_mark)
		return node.value
	def construct_sequence(self,node,deep=_B):
		if not isinstance(node,SequenceNode):raise ConstructorError(_A,_A,_e%node.id,node.start_mark)
		return[self.construct_object(child,deep=deep)for child in node.value]
	def construct_mapping(self,node,deep=_B):
		if not isinstance(node,MappingNode):raise ConstructorError(_A,_A,_N%node.id,node.start_mark)
		total_mapping=self.yaml_base_dict_type()
		if getattr(node,'merge',_A)is not _A:todo=[(node.merge,_B),(node.value,_B)]
		else:todo=[(node.value,_C)]
		for(values,check)in todo:
			mapping=self.yaml_base_dict_type()
			for(key_node,value_node)in values:
				key=self.construct_object(key_node,deep=_C)
				if not isinstance(key,Hashable):
					if isinstance(key,list):key=tuple(key)
				if PY2:
					try:hash(key)
					except TypeError as exc:raise ConstructorError(_E,node.start_mark,_U%exc,key_node.start_mark)
				elif not isinstance(key,Hashable):raise ConstructorError(_E,node.start_mark,_V,key_node.start_mark)
				value=self.construct_object(value_node,deep=deep)
				if check:
					if self.check_mapping_key(node,key_node,mapping,key,value):mapping[key]=value
				else:mapping[key]=value
			total_mapping.update(mapping)
		return total_mapping
	def check_mapping_key(self,node,key_node,mapping,key,value):
		if key in mapping:
			if not self.allow_duplicate_keys:
				mk=mapping.get(key)
				if PY2:
					if isinstance(key,unicode):key=key.encode(_O)
					if isinstance(value,unicode):value=value.encode(_O)
					if isinstance(mk,unicode):mk=mk.encode(_O)
				args=[_E,node.start_mark,'found duplicate key "{}" with value "{}" (original value: "{}")'.format(key,value,mk),key_node.start_mark,_f,_g]
				if self.allow_duplicate_keys is _A:warnings.warn(DuplicateKeyFutureWarning(*args))
				else:raise DuplicateKeyError(*args)
			return _B
		return _C
	def check_set_key(self,node,key_node,setting,key):
		if key in setting:
			if not self.allow_duplicate_keys:
				if PY2:
					if isinstance(key,unicode):key=key.encode(_O)
				args=['while constructing a set',node.start_mark,_W.format(key),key_node.start_mark,_f,_g]
				if self.allow_duplicate_keys is _A:warnings.warn(DuplicateKeyFutureWarning(*args))
				else:raise DuplicateKeyError(*args)
	def construct_pairs(self,node,deep=_B):
		if not isinstance(node,MappingNode):raise ConstructorError(_A,_A,_N%node.id,node.start_mark)
		pairs=[]
		for(key_node,value_node)in node.value:key=self.construct_object(key_node,deep=deep);value=self.construct_object(value_node,deep=deep);pairs.append((key,value))
		return pairs
	@classmethod
	def add_constructor(cls,tag,constructor):
		if'yaml_constructors'not in cls.__dict__:cls.yaml_constructors=cls.yaml_constructors.copy()
		cls.yaml_constructors[tag]=constructor
	@classmethod
	def add_multi_constructor(cls,tag_prefix,multi_constructor):
		if'yaml_multi_constructors'not in cls.__dict__:cls.yaml_multi_constructors=cls.yaml_multi_constructors.copy()
		cls.yaml_multi_constructors[tag_prefix]=multi_constructor
class SafeConstructor(BaseConstructor):
	def construct_scalar(self,node):
		if isinstance(node,MappingNode):
			for(key_node,value_node)in node.value:
				if key_node.tag==_X:return self.construct_scalar(value_node)
		return BaseConstructor.construct_scalar(self,node)
	def flatten_mapping(self,node):
		merge=[];index=0
		while index<len(node.value):
			key_node,value_node=node.value[index]
			if key_node.tag==_h:
				if merge:
					if self.allow_duplicate_keys:del node.value[index];index+=1;continue
					args=[_E,node.start_mark,_W.format(key_node.value),key_node.start_mark,_i,_j]
					if self.allow_duplicate_keys is _A:warnings.warn(DuplicateKeyFutureWarning(*args))
					else:raise DuplicateKeyError(*args)
				del node.value[index]
				if isinstance(value_node,MappingNode):self.flatten_mapping(value_node);merge.extend(value_node.value)
				elif isinstance(value_node,SequenceNode):
					submerge=[]
					for subnode in value_node.value:
						if not isinstance(subnode,MappingNode):raise ConstructorError(_E,node.start_mark,_k%subnode.id,subnode.start_mark)
						self.flatten_mapping(subnode);submerge.append(subnode.value)
					submerge.reverse()
					for value in submerge:merge.extend(value)
				else:raise ConstructorError(_E,node.start_mark,_l%value_node.id,value_node.start_mark)
			elif key_node.tag==_X:key_node.tag=_P;index+=1
			else:index+=1
		if bool(merge):node.merge=merge;node.value=merge+node.value
	def construct_mapping(self,node,deep=_B):
		if isinstance(node,MappingNode):self.flatten_mapping(node)
		return BaseConstructor.construct_mapping(self,node,deep=deep)
	def construct_yaml_null(self,node):self.construct_scalar(node)
	bool_values={'yes':_C,'no':_B,'y':_C,'n':_B,'true':_C,'false':_B,'on':_C,'off':_B}
	def construct_yaml_bool(self,node):value=self.construct_scalar(node);return self.bool_values[value.lower()]
	def construct_yaml_int(self,node):
		value_s=to_str(self.construct_scalar(node));value_s=value_s.replace(_D,'');sign=+1
		if value_s[0]=='-':sign=-1
		if value_s[0]in _L:value_s=value_s[1:]
		if value_s==_F:return 0
		elif value_s.startswith('0b'):return sign*int(value_s[2:],2)
		elif value_s.startswith('0x'):return sign*int(value_s[2:],16)
		elif value_s.startswith('0o'):return sign*int(value_s[2:],8)
		elif self.resolver.processing_version==(1,1)and value_s[0]==_F:return sign*int(value_s,8)
		elif self.resolver.processing_version==(1,1)and _G in value_s:
			digits=[int(part)for part in value_s.split(_G)];digits.reverse();base=1;value=0
			for digit in digits:value+=digit*base;base*=60
			return sign*value
		else:return sign*int(value_s)
	inf_value=1e300
	while inf_value!=inf_value*inf_value:inf_value*=inf_value
	nan_value=-inf_value/inf_value
	def construct_yaml_float(self,node):
		value_so=to_str(self.construct_scalar(node));value_s=value_so.replace(_D,'').lower();sign=+1
		if value_s[0]=='-':sign=-1
		if value_s[0]in _L:value_s=value_s[1:]
		if value_s=='.inf':return sign*self.inf_value
		elif value_s=='.nan':return self.nan_value
		elif self.resolver.processing_version!=(1,2)and _G in value_s:
			digits=[float(part)for part in value_s.split(_G)];digits.reverse();base=1;value=.0
			for digit in digits:value+=digit*base;base*=60
			return sign*value
		else:
			if self.resolver.processing_version!=(1,2)and'e'in value_s:
				mantissa,exponent=value_s.split('e')
				if _H not in mantissa:warnings.warn(MantissaNoDotYAML1_1Warning(node,value_so))
			return sign*float(value_s)
	if PY3:
		def construct_yaml_binary(self,node):
			try:value=self.construct_scalar(node).encode(_Q)
			except UnicodeEncodeError as exc:raise ConstructorError(_A,_A,_m%exc,node.start_mark)
			try:
				if hasattr(base64,_n):return base64.decodebytes(value)
				else:return base64.decodestring(value)
			except binascii.Error as exc:raise ConstructorError(_A,_A,_Y%exc,node.start_mark)
	else:
		def construct_yaml_binary(self,node):
			value=self.construct_scalar(node)
			try:return to_str(value).decode('base64')
			except(binascii.Error,UnicodeEncodeError)as exc:raise ConstructorError(_A,_A,_Y%exc,node.start_mark)
	timestamp_regexp=RegExp('^(?P<year>[0-9][0-9][0-9][0-9])\n          -(?P<month>[0-9][0-9]?)\n          -(?P<day>[0-9][0-9]?)\n          (?:((?P<t>[Tt])|[ \\t]+)   # explictly not retaining extra spaces\n          (?P<hour>[0-9][0-9]?)\n          :(?P<minute>[0-9][0-9])\n          :(?P<second>[0-9][0-9])\n          (?:\\.(?P<fraction>[0-9]*))?\n          (?:[ \\t]*(?P<tz>Z|(?P<tz_sign>[-+])(?P<tz_hour>[0-9][0-9]?)\n          (?::(?P<tz_minute>[0-9][0-9]))?))?)?$',re.X)
	def construct_yaml_timestamp(self,node,values=_A):
		if values is _A:
			try:match=self.timestamp_regexp.match(node.value)
			except TypeError:match=_A
			if match is _A:raise ConstructorError(_A,_A,_o.format(node.value),node.start_mark)
			values=match.groupdict()
		year=int(values['year']);month=int(values['month']);day=int(values['day'])
		if not values[_R]:return datetime.date(year,month,day)
		hour=int(values[_R]);minute=int(values[_p]);second=int(values[_q]);fraction=0
		if values[_I]:
			fraction_s=values[_I][:6]
			while len(fraction_s)<6:fraction_s+=_F
			fraction=int(fraction_s)
			if len(values[_I])>6 and int(values[_I][6])>4:fraction+=1
		delta=_A
		if values[_J]:
			tz_hour=int(values[_S]);minutes=values[_M];tz_minute=int(minutes)if minutes else 0;delta=datetime.timedelta(hours=tz_hour,minutes=tz_minute)
			if values[_J]=='-':delta=-delta
		data=datetime.datetime(year,month,day,hour,minute,second,fraction)
		if delta:data-=delta
		return data
	def construct_yaml_omap(self,node):
		omap=ordereddict();yield omap
		if not isinstance(node,SequenceNode):raise ConstructorError(_K,node.start_mark,_Z%node.id,node.start_mark)
		for subnode in node.value:
			if not isinstance(subnode,MappingNode):raise ConstructorError(_K,node.start_mark,_a%subnode.id,subnode.start_mark)
			if len(subnode.value)!=1:raise ConstructorError(_K,node.start_mark,_b%len(subnode.value),subnode.start_mark)
			key_node,value_node=subnode.value[0];key=self.construct_object(key_node);assert key not in omap;value=self.construct_object(value_node);omap[key]=value
	def construct_yaml_pairs(self,node):
		A='while constructing pairs';pairs=[];yield pairs
		if not isinstance(node,SequenceNode):raise ConstructorError(A,node.start_mark,_Z%node.id,node.start_mark)
		for subnode in node.value:
			if not isinstance(subnode,MappingNode):raise ConstructorError(A,node.start_mark,_a%subnode.id,subnode.start_mark)
			if len(subnode.value)!=1:raise ConstructorError(A,node.start_mark,_b%len(subnode.value),subnode.start_mark)
			key_node,value_node=subnode.value[0];key=self.construct_object(key_node);value=self.construct_object(value_node);pairs.append((key,value))
	def construct_yaml_set(self,node):data=set();yield data;value=self.construct_mapping(node);data.update(value)
	def construct_yaml_str(self,node):
		value=self.construct_scalar(node)
		if PY3:return value
		try:return value.encode(_Q)
		except UnicodeEncodeError:return value
	def construct_yaml_seq(self,node):data=self.yaml_base_list_type();yield data;data.extend(self.construct_sequence(node))
	def construct_yaml_map(self,node):data=self.yaml_base_dict_type();yield data;value=self.construct_mapping(node);data.update(value)
	def construct_yaml_object(self,node,cls):
		data=cls.__new__(cls);yield data
		if hasattr(data,_T):state=self.construct_mapping(node,deep=_C);data.__setstate__(state)
		else:state=self.construct_mapping(node);data.__dict__.update(state)
	def construct_undefined(self,node):raise ConstructorError(_A,_A,_r%utf8(node.tag),node.start_mark)
SafeConstructor.add_constructor(_s,SafeConstructor.construct_yaml_null)
SafeConstructor.add_constructor(_t,SafeConstructor.construct_yaml_bool)
SafeConstructor.add_constructor(_u,SafeConstructor.construct_yaml_int)
SafeConstructor.add_constructor(_v,SafeConstructor.construct_yaml_float)
SafeConstructor.add_constructor(_w,SafeConstructor.construct_yaml_binary)
SafeConstructor.add_constructor(_x,SafeConstructor.construct_yaml_timestamp)
SafeConstructor.add_constructor(_y,SafeConstructor.construct_yaml_omap)
SafeConstructor.add_constructor(_z,SafeConstructor.construct_yaml_pairs)
SafeConstructor.add_constructor(_A0,SafeConstructor.construct_yaml_set)
SafeConstructor.add_constructor(_P,SafeConstructor.construct_yaml_str)
SafeConstructor.add_constructor(_A1,SafeConstructor.construct_yaml_seq)
SafeConstructor.add_constructor(_A2,SafeConstructor.construct_yaml_map)
SafeConstructor.add_constructor(_A,SafeConstructor.construct_undefined)
if PY2:
	class classobj:0
class Constructor(SafeConstructor):
	def construct_python_str(self,node):return utf8(self.construct_scalar(node))
	def construct_python_unicode(self,node):return self.construct_scalar(node)
	if PY3:
		def construct_python_bytes(self,node):
			try:value=self.construct_scalar(node).encode(_Q)
			except UnicodeEncodeError as exc:raise ConstructorError(_A,_A,_m%exc,node.start_mark)
			try:
				if hasattr(base64,_n):return base64.decodebytes(value)
				else:return base64.decodestring(value)
			except binascii.Error as exc:raise ConstructorError(_A,_A,_Y%exc,node.start_mark)
	def construct_python_long(self,node):
		val=self.construct_yaml_int(node)
		if PY3:return val
		return int(val)
	def construct_python_complex(self,node):return complex(self.construct_scalar(node))
	def construct_python_tuple(self,node):return tuple(self.construct_sequence(node))
	def find_python_module(self,name,mark):
		if not name:raise ConstructorError(_c,mark,_A3,mark)
		try:__import__(name)
		except ImportError as exc:raise ConstructorError(_c,mark,_A4%(utf8(name),exc),mark)
		return sys.modules[name]
	def find_python_name(self,name,mark):
		A='while constructing a Python object'
		if not name:raise ConstructorError(A,mark,_A3,mark)
		if _H in name:
			lname=name.split(_H);lmodule_name=lname;lobject_name=[]
			while len(lmodule_name)>1:
				lobject_name.insert(0,lmodule_name.pop());module_name=_H.join(lmodule_name)
				try:__import__(module_name);break
				except ImportError:continue
		else:module_name=builtins_module;lobject_name=[name]
		try:__import__(module_name)
		except ImportError as exc:raise ConstructorError(A,mark,_A4%(utf8(module_name),exc),mark)
		module=sys.modules[module_name];object_name=_H.join(lobject_name);obj=module
		while lobject_name:
			if not hasattr(obj,lobject_name[0]):raise ConstructorError(A,mark,'cannot find %r in the module %r'%(utf8(object_name),module.__name__),mark)
			obj=getattr(obj,lobject_name.pop(0))
		return obj
	def construct_python_name(self,suffix,node):
		value=self.construct_scalar(node)
		if value:raise ConstructorError('while constructing a Python name',node.start_mark,_A5%utf8(value),node.start_mark)
		return self.find_python_name(suffix,node.start_mark)
	def construct_python_module(self,suffix,node):
		value=self.construct_scalar(node)
		if value:raise ConstructorError(_c,node.start_mark,_A5%utf8(value),node.start_mark)
		return self.find_python_module(suffix,node.start_mark)
	def make_python_instance(self,suffix,node,args=_A,kwds=_A,newobj=_B):
		if not args:args=[]
		if not kwds:kwds={}
		cls=self.find_python_name(suffix,node.start_mark)
		if PY3:
			if newobj and isinstance(cls,type):return cls.__new__(cls,*args,**kwds)
			else:return cls(*args,**kwds)
		elif newobj and isinstance(cls,type(classobj))and not args and not kwds:instance=classobj();instance.__class__=cls;return instance
		elif newobj and isinstance(cls,type):return cls.__new__(cls,*args,**kwds)
		else:return cls(*args,**kwds)
	def set_python_instance_state(self,instance,state):
		if hasattr(instance,_T):instance.__setstate__(state)
		else:
			slotstate={}
			if isinstance(state,tuple)and len(state)==2:state,slotstate=state
			if hasattr(instance,'__dict__'):instance.__dict__.update(state)
			elif state:slotstate.update(state)
			for(key,value)in slotstate.items():setattr(instance,key,value)
	def construct_python_object(self,suffix,node):instance=self.make_python_instance(suffix,node,newobj=_C);self.recursive_objects[node]=instance;yield instance;deep=hasattr(instance,_T);state=self.construct_mapping(node,deep=deep);self.set_python_instance_state(instance,state)
	def construct_python_object_apply(self,suffix,node,newobj=_B):
		if isinstance(node,SequenceNode):args=self.construct_sequence(node,deep=_C);kwds={};state={};listitems=[];dictitems={}
		else:value=self.construct_mapping(node,deep=_C);args=value.get('args',[]);kwds=value.get('kwds',{});state=value.get('state',{});listitems=value.get('listitems',[]);dictitems=value.get('dictitems',{})
		instance=self.make_python_instance(suffix,node,args,kwds,newobj)
		if bool(state):self.set_python_instance_state(instance,state)
		if bool(listitems):instance.extend(listitems)
		if bool(dictitems):
			for key in dictitems:instance[key]=dictitems[key]
		return instance
	def construct_python_object_new(self,suffix,node):return self.construct_python_object_apply(suffix,node,newobj=_C)
Constructor.add_constructor('tag:yaml.org,2002:python/none',Constructor.construct_yaml_null)
Constructor.add_constructor('tag:yaml.org,2002:python/bool',Constructor.construct_yaml_bool)
Constructor.add_constructor('tag:yaml.org,2002:python/str',Constructor.construct_python_str)
Constructor.add_constructor('tag:yaml.org,2002:python/unicode',Constructor.construct_python_unicode)
if PY3:Constructor.add_constructor('tag:yaml.org,2002:python/bytes',Constructor.construct_python_bytes)
Constructor.add_constructor('tag:yaml.org,2002:python/int',Constructor.construct_yaml_int)
Constructor.add_constructor('tag:yaml.org,2002:python/long',Constructor.construct_python_long)
Constructor.add_constructor('tag:yaml.org,2002:python/float',Constructor.construct_yaml_float)
Constructor.add_constructor('tag:yaml.org,2002:python/complex',Constructor.construct_python_complex)
Constructor.add_constructor('tag:yaml.org,2002:python/list',Constructor.construct_yaml_seq)
Constructor.add_constructor('tag:yaml.org,2002:python/tuple',Constructor.construct_python_tuple)
Constructor.add_constructor('tag:yaml.org,2002:python/dict',Constructor.construct_yaml_map)
Constructor.add_multi_constructor('tag:yaml.org,2002:python/name:',Constructor.construct_python_name)
Constructor.add_multi_constructor('tag:yaml.org,2002:python/module:',Constructor.construct_python_module)
Constructor.add_multi_constructor('tag:yaml.org,2002:python/object:',Constructor.construct_python_object)
Constructor.add_multi_constructor('tag:yaml.org,2002:python/object/apply:',Constructor.construct_python_object_apply)
Constructor.add_multi_constructor('tag:yaml.org,2002:python/object/new:',Constructor.construct_python_object_new)
class RoundTripConstructor(SafeConstructor):
	def construct_scalar(self,node):
		A='\x07'
		if not isinstance(node,ScalarNode):raise ConstructorError(_A,_A,_d%node.id,node.start_mark)
		if node.style=='|'and isinstance(node.value,text_type):
			lss=LiteralScalarString(node.value,anchor=node.anchor)
			if node.comment and node.comment[1]:lss.comment=node.comment[1][0]
			return lss
		if node.style=='>'and isinstance(node.value,text_type):
			fold_positions=[];idx=-1
			while _C:
				idx=node.value.find(A,idx+1)
				if idx<0:break
				fold_positions.append(idx-len(fold_positions))
			fss=FoldedScalarString(node.value.replace(A,''),anchor=node.anchor)
			if node.comment and node.comment[1]:fss.comment=node.comment[1][0]
			if fold_positions:fss.fold_pos=fold_positions
			return fss
		elif bool(self._preserve_quotes)and isinstance(node.value,text_type):
			if node.style=="'":return SingleQuotedScalarString(node.value,anchor=node.anchor)
			if node.style=='"':return DoubleQuotedScalarString(node.value,anchor=node.anchor)
		if node.anchor:return PlainScalarString(node.value,anchor=node.anchor)
		return node.value
	def construct_yaml_int(self,node):
		width=_A;value_su=to_str(self.construct_scalar(node))
		try:sx=value_su.rstrip(_D);underscore=[len(sx)-sx.rindex(_D)-1,_B,_B]
		except ValueError:underscore=_A
		except IndexError:underscore=_A
		value_s=value_su.replace(_D,'');sign=+1
		if value_s[0]=='-':sign=-1
		if value_s[0]in _L:value_s=value_s[1:]
		if value_s==_F:return 0
		elif value_s.startswith('0b'):
			if self.resolver.processing_version>(1,1)and value_s[2]==_F:width=len(value_s[2:])
			if underscore is not _A:underscore[1]=value_su[2]==_D;underscore[2]=len(value_su[2:])>1 and value_su[-1]==_D
			return BinaryInt(sign*int(value_s[2:],2),width=width,underscore=underscore,anchor=node.anchor)
		elif value_s.startswith('0x'):
			if self.resolver.processing_version>(1,1)and value_s[2]==_F:width=len(value_s[2:])
			hex_fun=HexInt
			for ch in value_s[2:]:
				if ch in'ABCDEF':hex_fun=HexCapsInt;break
				if ch in'abcdef':break
			if underscore is not _A:underscore[1]=value_su[2]==_D;underscore[2]=len(value_su[2:])>1 and value_su[-1]==_D
			return hex_fun(sign*int(value_s[2:],16),width=width,underscore=underscore,anchor=node.anchor)
		elif value_s.startswith('0o'):
			if self.resolver.processing_version>(1,1)and value_s[2]==_F:width=len(value_s[2:])
			if underscore is not _A:underscore[1]=value_su[2]==_D;underscore[2]=len(value_su[2:])>1 and value_su[-1]==_D
			return OctalInt(sign*int(value_s[2:],8),width=width,underscore=underscore,anchor=node.anchor)
		elif self.resolver.processing_version!=(1,2)and value_s[0]==_F:return sign*int(value_s,8)
		elif self.resolver.processing_version!=(1,2)and _G in value_s:
			digits=[int(part)for part in value_s.split(_G)];digits.reverse();base=1;value=0
			for digit in digits:value+=digit*base;base*=60
			return sign*value
		elif self.resolver.processing_version>(1,1)and value_s[0]==_F:
			if underscore is not _A:underscore[2]=len(value_su)>1 and value_su[-1]==_D
			return ScalarInt(sign*int(value_s),width=len(value_s),underscore=underscore)
		elif underscore:underscore[2]=len(value_su)>1 and value_su[-1]==_D;return ScalarInt(sign*int(value_s),width=_A,underscore=underscore,anchor=node.anchor)
		elif node.anchor:return ScalarInt(sign*int(value_s),width=_A,anchor=node.anchor)
		else:return sign*int(value_s)
	def construct_yaml_float(self,node):
		def leading_zeros(v):
			lead0=0;idx=0
			while idx<len(v)and v[idx]in'0.':
				if v[idx]==_F:lead0+=1
				idx+=1
			return lead0
		m_sign=_B;value_so=to_str(self.construct_scalar(node));value_s=value_so.replace(_D,'').lower();sign=+1
		if value_s[0]=='-':sign=-1
		if value_s[0]in _L:m_sign=value_s[0];value_s=value_s[1:]
		if value_s=='.inf':return sign*self.inf_value
		if value_s=='.nan':return self.nan_value
		if self.resolver.processing_version!=(1,2)and _G in value_s:
			digits=[float(part)for part in value_s.split(_G)];digits.reverse();base=1;value=.0
			for digit in digits:value+=digit*base;base*=60
			return sign*value
		if'e'in value_s:
			try:mantissa,exponent=value_so.split('e');exp='e'
			except ValueError:mantissa,exponent=value_so.split('E');exp='E'
			if self.resolver.processing_version!=(1,2):
				if _H not in mantissa:warnings.warn(MantissaNoDotYAML1_1Warning(node,value_so))
			lead0=leading_zeros(mantissa);width=len(mantissa);prec=mantissa.find(_H)
			if m_sign:width-=1
			e_width=len(exponent);e_sign=exponent[0]in _L;return ScalarFloat(sign*float(value_s),width=width,prec=prec,m_sign=m_sign,m_lead0=lead0,exp=exp,e_width=e_width,e_sign=e_sign,anchor=node.anchor)
		width=len(value_so);prec=value_so.index(_H);lead0=leading_zeros(value_so);return ScalarFloat(sign*float(value_s),width=width,prec=prec,m_sign=m_sign,m_lead0=lead0,anchor=node.anchor)
	def construct_yaml_str(self,node):
		value=self.construct_scalar(node)
		if isinstance(value,ScalarString):return value
		if PY3:return value
		try:return value.encode(_Q)
		except AttributeError:return value
		except UnicodeEncodeError:return value
	def construct_rt_sequence(self,node,seqtyp,deep=_B):
		if not isinstance(node,SequenceNode):raise ConstructorError(_A,_A,_e%node.id,node.start_mark)
		ret_val=[]
		if node.comment:
			seqtyp._yaml_add_comment(node.comment[:2])
			if len(node.comment)>2:seqtyp.yaml_end_comment_extend(node.comment[2],clear=_C)
		if node.anchor:
			from dynaconf.vendor.ruamel.yaml.serializer import templated_id
			if not templated_id(node.anchor):seqtyp.yaml_set_anchor(node.anchor)
		for(idx,child)in enumerate(node.value):
			if child.comment:seqtyp._yaml_add_comment(child.comment,key=idx);child.comment=_A
			ret_val.append(self.construct_object(child,deep=deep));seqtyp._yaml_set_idx_line_col(idx,[child.start_mark.line,child.start_mark.column])
		return ret_val
	def flatten_mapping(self,node):
		def constructed(value_node):
			if value_node in self.constructed_objects:value=self.constructed_objects[value_node]
			else:value=self.construct_object(value_node,deep=_B)
			return value
		merge_map_list=[];index=0
		while index<len(node.value):
			key_node,value_node=node.value[index]
			if key_node.tag==_h:
				if merge_map_list:
					if self.allow_duplicate_keys:del node.value[index];index+=1;continue
					args=[_E,node.start_mark,_W.format(key_node.value),key_node.start_mark,_i,_j]
					if self.allow_duplicate_keys is _A:warnings.warn(DuplicateKeyFutureWarning(*args))
					else:raise DuplicateKeyError(*args)
				del node.value[index]
				if isinstance(value_node,MappingNode):merge_map_list.append((index,constructed(value_node)))
				elif isinstance(value_node,SequenceNode):
					for subnode in value_node.value:
						if not isinstance(subnode,MappingNode):raise ConstructorError(_E,node.start_mark,_k%subnode.id,subnode.start_mark)
						merge_map_list.append((index,constructed(subnode)))
				else:raise ConstructorError(_E,node.start_mark,_l%value_node.id,value_node.start_mark)
			elif key_node.tag==_X:key_node.tag=_P;index+=1
			else:index+=1
		return merge_map_list
	def _sentinel(self):0
	def construct_mapping(self,node,maptyp,deep=_B):
		if not isinstance(node,MappingNode):raise ConstructorError(_A,_A,_N%node.id,node.start_mark)
		merge_map=self.flatten_mapping(node)
		if node.comment:
			maptyp._yaml_add_comment(node.comment[:2])
			if len(node.comment)>2:maptyp.yaml_end_comment_extend(node.comment[2],clear=_C)
		if node.anchor:
			from dynaconf.vendor.ruamel.yaml.serializer import templated_id
			if not templated_id(node.anchor):maptyp.yaml_set_anchor(node.anchor)
		last_key,last_value=_A,self._sentinel
		for(key_node,value_node)in node.value:
			key=self.construct_object(key_node,deep=_C)
			if not isinstance(key,Hashable):
				if isinstance(key,MutableSequence):
					key_s=CommentedKeySeq(key)
					if key_node.flow_style is _C:key_s.fa.set_flow_style()
					elif key_node.flow_style is _B:key_s.fa.set_block_style()
					key=key_s
				elif isinstance(key,MutableMapping):
					key_m=CommentedKeyMap(key)
					if key_node.flow_style is _C:key_m.fa.set_flow_style()
					elif key_node.flow_style is _B:key_m.fa.set_block_style()
					key=key_m
			if PY2:
				try:hash(key)
				except TypeError as exc:raise ConstructorError(_E,node.start_mark,_U%exc,key_node.start_mark)
			elif not isinstance(key,Hashable):raise ConstructorError(_E,node.start_mark,_V,key_node.start_mark)
			value=self.construct_object(value_node,deep=deep)
			if self.check_mapping_key(node,key_node,maptyp,key,value):
				if key_node.comment and len(key_node.comment)>4 and key_node.comment[4]:
					if last_value is _A:key_node.comment[0]=key_node.comment.pop(4);maptyp._yaml_add_comment(key_node.comment,value=last_key)
					else:key_node.comment[2]=key_node.comment.pop(4);maptyp._yaml_add_comment(key_node.comment,key=key)
					key_node.comment=_A
				if key_node.comment:maptyp._yaml_add_comment(key_node.comment,key=key)
				if value_node.comment:maptyp._yaml_add_comment(value_node.comment,value=key)
				maptyp._yaml_set_kv_line_col(key,[key_node.start_mark.line,key_node.start_mark.column,value_node.start_mark.line,value_node.start_mark.column]);maptyp[key]=value;last_key,last_value=key,value
		if merge_map:maptyp.add_yaml_merge(merge_map)
	def construct_setting(self,node,typ,deep=_B):
		if not isinstance(node,MappingNode):raise ConstructorError(_A,_A,_N%node.id,node.start_mark)
		if node.comment:
			typ._yaml_add_comment(node.comment[:2])
			if len(node.comment)>2:typ.yaml_end_comment_extend(node.comment[2],clear=_C)
		if node.anchor:
			from dynaconf.vendor.ruamel.yaml.serializer import templated_id
			if not templated_id(node.anchor):typ.yaml_set_anchor(node.anchor)
		for(key_node,value_node)in node.value:
			key=self.construct_object(key_node,deep=_C)
			if not isinstance(key,Hashable):
				if isinstance(key,list):key=tuple(key)
			if PY2:
				try:hash(key)
				except TypeError as exc:raise ConstructorError(_E,node.start_mark,_U%exc,key_node.start_mark)
			elif not isinstance(key,Hashable):raise ConstructorError(_E,node.start_mark,_V,key_node.start_mark)
			value=self.construct_object(value_node,deep=deep);self.check_set_key(node,key_node,typ,key)
			if key_node.comment:typ._yaml_add_comment(key_node.comment,key=key)
			if value_node.comment:typ._yaml_add_comment(value_node.comment,value=key)
			typ.add(key)
	def construct_yaml_seq(self,node):
		data=CommentedSeq();data._yaml_set_line_col(node.start_mark.line,node.start_mark.column)
		if node.comment:data._yaml_add_comment(node.comment)
		yield data;data.extend(self.construct_rt_sequence(node,data));self.set_collection_style(data,node)
	def construct_yaml_map(self,node):data=CommentedMap();data._yaml_set_line_col(node.start_mark.line,node.start_mark.column);yield data;self.construct_mapping(node,data,deep=_C);self.set_collection_style(data,node)
	def set_collection_style(self,data,node):
		if len(data)==0:return
		if node.flow_style is _C:data.fa.set_flow_style()
		elif node.flow_style is _B:data.fa.set_block_style()
	def construct_yaml_object(self,node,cls):
		data=cls.__new__(cls);yield data
		if hasattr(data,_T):state=SafeConstructor.construct_mapping(self,node,deep=_C);data.__setstate__(state)
		else:state=SafeConstructor.construct_mapping(self,node);data.__dict__.update(state)
	def construct_yaml_omap(self,node):
		omap=CommentedOrderedMap();omap._yaml_set_line_col(node.start_mark.line,node.start_mark.column)
		if node.flow_style is _C:omap.fa.set_flow_style()
		elif node.flow_style is _B:omap.fa.set_block_style()
		yield omap
		if node.comment:
			omap._yaml_add_comment(node.comment[:2])
			if len(node.comment)>2:omap.yaml_end_comment_extend(node.comment[2],clear=_C)
		if not isinstance(node,SequenceNode):raise ConstructorError(_K,node.start_mark,_Z%node.id,node.start_mark)
		for subnode in node.value:
			if not isinstance(subnode,MappingNode):raise ConstructorError(_K,node.start_mark,_a%subnode.id,subnode.start_mark)
			if len(subnode.value)!=1:raise ConstructorError(_K,node.start_mark,_b%len(subnode.value),subnode.start_mark)
			key_node,value_node=subnode.value[0];key=self.construct_object(key_node);assert key not in omap;value=self.construct_object(value_node)
			if key_node.comment:omap._yaml_add_comment(key_node.comment,key=key)
			if subnode.comment:omap._yaml_add_comment(subnode.comment,key=key)
			if value_node.comment:omap._yaml_add_comment(value_node.comment,value=key)
			omap[key]=value
	def construct_yaml_set(self,node):data=CommentedSet();data._yaml_set_line_col(node.start_mark.line,node.start_mark.column);yield data;self.construct_setting(node,data)
	def construct_undefined(self,node):
		try:
			if isinstance(node,MappingNode):
				data=CommentedMap();data._yaml_set_line_col(node.start_mark.line,node.start_mark.column)
				if node.flow_style is _C:data.fa.set_flow_style()
				elif node.flow_style is _B:data.fa.set_block_style()
				data.yaml_set_tag(node.tag);yield data
				if node.anchor:data.yaml_set_anchor(node.anchor)
				self.construct_mapping(node,data);return
			elif isinstance(node,ScalarNode):
				data2=TaggedScalar();data2.value=self.construct_scalar(node);data2.style=node.style;data2.yaml_set_tag(node.tag);yield data2
				if node.anchor:data2.yaml_set_anchor(node.anchor,always_dump=_C)
				return
			elif isinstance(node,SequenceNode):
				data3=CommentedSeq();data3._yaml_set_line_col(node.start_mark.line,node.start_mark.column)
				if node.flow_style is _C:data3.fa.set_flow_style()
				elif node.flow_style is _B:data3.fa.set_block_style()
				data3.yaml_set_tag(node.tag);yield data3
				if node.anchor:data3.yaml_set_anchor(node.anchor)
				data3.extend(self.construct_sequence(node));return
		except:pass
		raise ConstructorError(_A,_A,_r%utf8(node.tag),node.start_mark)
	def construct_yaml_timestamp(self,node,values=_A):
		B='t';A='tz'
		try:match=self.timestamp_regexp.match(node.value)
		except TypeError:match=_A
		if match is _A:raise ConstructorError(_A,_A,_o.format(node.value),node.start_mark)
		values=match.groupdict()
		if not values[_R]:return SafeConstructor.construct_yaml_timestamp(self,node,values)
		for part in[B,_J,_S,_M]:
			if values[part]:break
		else:return SafeConstructor.construct_yaml_timestamp(self,node,values)
		year=int(values['year']);month=int(values['month']);day=int(values['day']);hour=int(values[_R]);minute=int(values[_p]);second=int(values[_q]);fraction=0
		if values[_I]:
			fraction_s=values[_I][:6]
			while len(fraction_s)<6:fraction_s+=_F
			fraction=int(fraction_s)
			if len(values[_I])>6 and int(values[_I][6])>4:fraction+=1
		delta=_A
		if values[_J]:
			tz_hour=int(values[_S]);minutes=values[_M];tz_minute=int(minutes)if minutes else 0;delta=datetime.timedelta(hours=tz_hour,minutes=tz_minute)
			if values[_J]=='-':delta=-delta
		if delta:
			dt=datetime.datetime(year,month,day,hour,minute);dt-=delta;data=TimeStamp(dt.year,dt.month,dt.day,dt.hour,dt.minute,second,fraction);data._yaml['delta']=delta;tz=values[_J]+values[_S]
			if values[_M]:tz+=_G+values[_M]
			data._yaml[A]=tz
		else:
			data=TimeStamp(year,month,day,hour,minute,second,fraction)
			if values[A]:data._yaml[A]=values[A]
		if values[B]:data._yaml[B]=_C
		return data
	def construct_yaml_bool(self,node):
		b=SafeConstructor.construct_yaml_bool(self,node)
		if node.anchor:return ScalarBoolean(b,anchor=node.anchor)
		return b
RoundTripConstructor.add_constructor(_s,RoundTripConstructor.construct_yaml_null)
RoundTripConstructor.add_constructor(_t,RoundTripConstructor.construct_yaml_bool)
RoundTripConstructor.add_constructor(_u,RoundTripConstructor.construct_yaml_int)
RoundTripConstructor.add_constructor(_v,RoundTripConstructor.construct_yaml_float)
RoundTripConstructor.add_constructor(_w,RoundTripConstructor.construct_yaml_binary)
RoundTripConstructor.add_constructor(_x,RoundTripConstructor.construct_yaml_timestamp)
RoundTripConstructor.add_constructor(_y,RoundTripConstructor.construct_yaml_omap)
RoundTripConstructor.add_constructor(_z,RoundTripConstructor.construct_yaml_pairs)
RoundTripConstructor.add_constructor(_A0,RoundTripConstructor.construct_yaml_set)
RoundTripConstructor.add_constructor(_P,RoundTripConstructor.construct_yaml_str)
RoundTripConstructor.add_constructor(_A1,RoundTripConstructor.construct_yaml_seq)
RoundTripConstructor.add_constructor(_A2,RoundTripConstructor.construct_yaml_map)
RoundTripConstructor.add_constructor(_A,RoundTripConstructor.construct_undefined)
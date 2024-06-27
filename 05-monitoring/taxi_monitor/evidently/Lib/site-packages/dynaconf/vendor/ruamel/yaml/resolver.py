from __future__ import absolute_import
_H='yaml_implicit_resolvers'
_G='-+0123456789'
_F='tag:yaml.org,2002:int'
_E='-+0123456789.'
_D='tag:yaml.org,2002:float'
_C='tag:yaml.org,2002:bool'
_B=False
_A=None
import re
if _B:from typing import Any,Dict,List,Union,Text,Optional;from.compat import VersionType
from.compat import string_types,_DEFAULT_YAML_VERSION
from.error import*
from.nodes import MappingNode,ScalarNode,SequenceNode
from.util import RegExp
__all__=['BaseResolver','Resolver','VersionedResolver']
implicit_resolvers=[([(1,2)],_C,RegExp('^(?:true|True|TRUE|false|False|FALSE)$',re.X),list('tTfF')),([(1,1)],_C,RegExp('^(?:y|Y|yes|Yes|YES|n|N|no|No|NO\n        |true|True|TRUE|false|False|FALSE\n        |on|On|ON|off|Off|OFF)$',re.X),list('yYnNtTfFoO')),([(1,2)],_D,RegExp('^(?:\n         [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?\n        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)\n        |[-+]?\\.[0-9_]+(?:[eE][-+][0-9]+)?\n        |[-+]?\\.(?:inf|Inf|INF)\n        |\\.(?:nan|NaN|NAN))$',re.X),list(_E)),([(1,1)],_D,RegExp('^(?:\n         [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?\n        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)\n        |\\.[0-9_]+(?:[eE][-+][0-9]+)?\n        |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*  # sexagesimal float\n        |[-+]?\\.(?:inf|Inf|INF)\n        |\\.(?:nan|NaN|NAN))$',re.X),list(_E)),([(1,2)],_F,RegExp('^(?:[-+]?0b[0-1_]+\n        |[-+]?0o?[0-7_]+\n        |[-+]?[0-9_]+\n        |[-+]?0x[0-9a-fA-F_]+)$',re.X),list(_G)),([(1,1)],_F,RegExp('^(?:[-+]?0b[0-1_]+\n        |[-+]?0?[0-7_]+\n        |[-+]?(?:0|[1-9][0-9_]*)\n        |[-+]?0x[0-9a-fA-F_]+\n        |[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+)$',re.X),list(_G)),([(1,2),(1,1)],'tag:yaml.org,2002:merge',RegExp('^(?:<<)$'),['<']),([(1,2),(1,1)],'tag:yaml.org,2002:null',RegExp('^(?: ~\n        |null|Null|NULL\n        | )$',re.X),['~','n','N','']),([(1,2),(1,1)],'tag:yaml.org,2002:timestamp',RegExp('^(?:[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\n        |[0-9][0-9][0-9][0-9] -[0-9][0-9]? -[0-9][0-9]?\n        (?:[Tt]|[ \\t]+)[0-9][0-9]?\n        :[0-9][0-9] :[0-9][0-9] (?:\\.[0-9]*)?\n        (?:[ \\t]*(?:Z|[-+][0-9][0-9]?(?::[0-9][0-9])?))?)$',re.X),list('0123456789')),([(1,2),(1,1)],'tag:yaml.org,2002:value',RegExp('^(?:=)$'),['=']),([(1,2),(1,1)],'tag:yaml.org,2002:yaml',RegExp('^(?:!|&|\\*)$'),list('!&*'))]
class ResolverError(YAMLError):0
class BaseResolver:
	DEFAULT_SCALAR_TAG='tag:yaml.org,2002:str';DEFAULT_SEQUENCE_TAG='tag:yaml.org,2002:seq';DEFAULT_MAPPING_TAG='tag:yaml.org,2002:map';yaml_implicit_resolvers={};yaml_path_resolvers={}
	def __init__(self,loadumper=_A):
		self.loadumper=loadumper
		if self.loadumper is not _A and getattr(self.loadumper,'_resolver',_A)is _A:self.loadumper._resolver=self.loadumper
		self._loader_version=_A;self.resolver_exact_paths=[];self.resolver_prefix_paths=[]
	@property
	def parser(self):
		if self.loadumper is not _A:
			if hasattr(self.loadumper,'typ'):return self.loadumper.parser
			return self.loadumper._parser
	@classmethod
	def add_implicit_resolver_base(cls,tag,regexp,first):
		if _H not in cls.__dict__:cls.yaml_implicit_resolvers=dict((k,cls.yaml_implicit_resolvers[k][:])for k in cls.yaml_implicit_resolvers)
		if first is _A:first=[_A]
		for ch in first:cls.yaml_implicit_resolvers.setdefault(ch,[]).append((tag,regexp))
	@classmethod
	def add_implicit_resolver(cls,tag,regexp,first):
		if _H not in cls.__dict__:cls.yaml_implicit_resolvers=dict((k,cls.yaml_implicit_resolvers[k][:])for k in cls.yaml_implicit_resolvers)
		if first is _A:first=[_A]
		for ch in first:cls.yaml_implicit_resolvers.setdefault(ch,[]).append((tag,regexp))
		implicit_resolvers.append(([(1,2),(1,1)],tag,regexp,first))
	@classmethod
	def add_path_resolver(cls,tag,path,kind=_A):
		if'yaml_path_resolvers'not in cls.__dict__:cls.yaml_path_resolvers=cls.yaml_path_resolvers.copy()
		new_path=[]
		for element in path:
			if isinstance(element,(list,tuple)):
				if len(element)==2:node_check,index_check=element
				elif len(element)==1:node_check=element[0];index_check=True
				else:raise ResolverError('Invalid path element: %s'%(element,))
			else:node_check=_A;index_check=element
			if node_check is str:node_check=ScalarNode
			elif node_check is list:node_check=SequenceNode
			elif node_check is dict:node_check=MappingNode
			elif node_check not in[ScalarNode,SequenceNode,MappingNode]and not isinstance(node_check,string_types)and node_check is not _A:raise ResolverError('Invalid node checker: %s'%(node_check,))
			if not isinstance(index_check,(string_types,int))and index_check is not _A:raise ResolverError('Invalid index checker: %s'%(index_check,))
			new_path.append((node_check,index_check))
		if kind is str:kind=ScalarNode
		elif kind is list:kind=SequenceNode
		elif kind is dict:kind=MappingNode
		elif kind not in[ScalarNode,SequenceNode,MappingNode]and kind is not _A:raise ResolverError('Invalid node kind: %s'%(kind,))
		cls.yaml_path_resolvers[(tuple(new_path),kind)]=tag
	def descend_resolver(self,current_node,current_index):
		if not self.yaml_path_resolvers:return
		exact_paths={};prefix_paths=[]
		if current_node:
			depth=len(self.resolver_prefix_paths)
			for(path,kind)in self.resolver_prefix_paths[-1]:
				if self.check_resolver_prefix(depth,path,kind,current_node,current_index):
					if len(path)>depth:prefix_paths.append((path,kind))
					else:exact_paths[kind]=self.yaml_path_resolvers[(path,kind)]
		else:
			for(path,kind)in self.yaml_path_resolvers:
				if not path:exact_paths[kind]=self.yaml_path_resolvers[(path,kind)]
				else:prefix_paths.append((path,kind))
		self.resolver_exact_paths.append(exact_paths);self.resolver_prefix_paths.append(prefix_paths)
	def ascend_resolver(self):
		if not self.yaml_path_resolvers:return
		self.resolver_exact_paths.pop();self.resolver_prefix_paths.pop()
	def check_resolver_prefix(self,depth,path,kind,current_node,current_index):
		node_check,index_check=path[depth-1]
		if isinstance(node_check,string_types):
			if current_node.tag!=node_check:return _B
		elif node_check is not _A:
			if not isinstance(current_node,node_check):return _B
		if index_check is True and current_index is not _A:return _B
		if(index_check is _B or index_check is _A)and current_index is _A:return _B
		if isinstance(index_check,string_types):
			if not(isinstance(current_index,ScalarNode)and index_check==current_index.value):return _B
		elif isinstance(index_check,int)and not isinstance(index_check,bool):
			if index_check!=current_index:return _B
		return True
	def resolve(self,kind,value,implicit):
		if kind is ScalarNode and implicit[0]:
			if value=='':resolvers=self.yaml_implicit_resolvers.get('',[])
			else:resolvers=self.yaml_implicit_resolvers.get(value[0],[])
			resolvers+=self.yaml_implicit_resolvers.get(_A,[])
			for(tag,regexp)in resolvers:
				if regexp.match(value):return tag
			implicit=implicit[1]
		if bool(self.yaml_path_resolvers):
			exact_paths=self.resolver_exact_paths[-1]
			if kind in exact_paths:return exact_paths[kind]
			if _A in exact_paths:return exact_paths[_A]
		if kind is ScalarNode:return self.DEFAULT_SCALAR_TAG
		elif kind is SequenceNode:return self.DEFAULT_SEQUENCE_TAG
		elif kind is MappingNode:return self.DEFAULT_MAPPING_TAG
	@property
	def processing_version(self):0
class Resolver(BaseResolver):0
for ir in implicit_resolvers:
	if(1,2)in ir[0]:Resolver.add_implicit_resolver_base(*ir[1:])
class VersionedResolver(BaseResolver):
	def __init__(self,version=_A,loader=_A,loadumper=_A):
		if loader is _A and loadumper is not _A:loader=loadumper
		BaseResolver.__init__(self,loader);self._loader_version=self.get_loader_version(version);self._version_implicit_resolver={}
	def add_version_implicit_resolver(self,version,tag,regexp,first):
		if first is _A:first=[_A]
		impl_resolver=self._version_implicit_resolver.setdefault(version,{})
		for ch in first:impl_resolver.setdefault(ch,[]).append((tag,regexp))
	def get_loader_version(self,version):
		if version is _A or isinstance(version,tuple):return version
		if isinstance(version,list):return tuple(version)
		return tuple(map(int,version.split('.')))
	@property
	def versioned_resolver(self):
		version=self.processing_version
		if version not in self._version_implicit_resolver:
			for x in implicit_resolvers:
				if version in x[0]:self.add_version_implicit_resolver(version,x[1],x[2],x[3])
		return self._version_implicit_resolver[version]
	def resolve(self,kind,value,implicit):
		if kind is ScalarNode and implicit[0]:
			if value=='':resolvers=self.versioned_resolver.get('',[])
			else:resolvers=self.versioned_resolver.get(value[0],[])
			resolvers+=self.versioned_resolver.get(_A,[])
			for(tag,regexp)in resolvers:
				if regexp.match(value):return tag
			implicit=implicit[1]
		if bool(self.yaml_path_resolvers):
			exact_paths=self.resolver_exact_paths[-1]
			if kind in exact_paths:return exact_paths[kind]
			if _A in exact_paths:return exact_paths[_A]
		if kind is ScalarNode:return self.DEFAULT_SCALAR_TAG
		elif kind is SequenceNode:return self.DEFAULT_SEQUENCE_TAG
		elif kind is MappingNode:return self.DEFAULT_MAPPING_TAG
	@property
	def processing_version(self):
		try:version=self.loadumper._scanner.yaml_version
		except AttributeError:
			try:
				if hasattr(self.loadumper,'typ'):version=self.loadumper.version
				else:version=self.loadumper._serializer.use_version
			except AttributeError:version=_A
		if version is _A:
			version=self._loader_version
			if version is _A:version=_DEFAULT_YAML_VERSION
		return version
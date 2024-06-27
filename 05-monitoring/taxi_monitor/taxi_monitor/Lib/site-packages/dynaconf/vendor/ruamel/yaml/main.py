from __future__ import absolute_import,unicode_literals,print_function
_L='_emitter'
_K='_serializer'
_J='{}.dump(_all) takes two positional argument but at least three were given ({!r})'
_I='_stream'
_H='{}.__init__() takes no positional argument but at least one was given ({!r})'
_G='yaml_tag'
_F='open'
_E='rt'
_D='_'
_C=True
_B=False
_A=None
import sys,os,warnings,glob
from importlib import import_module
import dynaconf.vendor.ruamel as ruamel
from.error import UnsafeLoaderWarning,YAMLError
from.tokens import*
from.events import*
from.nodes import*
from.loader import BaseLoader,SafeLoader,Loader,RoundTripLoader
from.dumper import BaseDumper,SafeDumper,Dumper,RoundTripDumper
from.compat import StringIO,BytesIO,with_metaclass,PY3,nprint
from.resolver import VersionedResolver,Resolver
from.representer import BaseRepresenter,SafeRepresenter,Representer,RoundTripRepresenter
from.constructor import BaseConstructor,SafeConstructor,Constructor,RoundTripConstructor
from.loader import Loader as UnsafeLoader
if _B:
	from typing import List,Set,Dict,Union,Any,Callable,Optional,Text;from.compat import StreamType,StreamTextType,VersionType
	if PY3:from pathlib import Path
	else:Path=Any
try:from _ruamel_yaml import CParser,CEmitter
except:CParser=CEmitter=_A
enforce=object()
class YAML:
	def __init__(self,_kw=enforce,typ=_A,pure=_B,output=_A,plug_ins=_A):
		if _kw is not enforce:raise TypeError(_H.format(self.__class__.__name__,_kw))
		self.typ=[_E]if typ is _A else typ if isinstance(typ,list)else[typ];self.pure=pure;self._output=output;self._context_manager=_A;self.plug_ins=[]
		for pu in([]if plug_ins is _A else plug_ins)+self.official_plug_ins():file_name=pu.replace(os.sep,'.');self.plug_ins.append(import_module(file_name))
		self.Resolver=ruamel.yaml.resolver.VersionedResolver;self.allow_unicode=_C;self.Reader=_A;self.Representer=_A;self.Constructor=_A;self.Scanner=_A;self.Serializer=_A;self.default_flow_style=_A;typ_found=1;setup_rt=_B
		if _E in self.typ:setup_rt=_C
		elif'safe'in self.typ:self.Emitter=ruamel.yaml.emitter.Emitter if pure or CEmitter is _A else CEmitter;self.Representer=ruamel.yaml.representer.SafeRepresenter;self.Parser=ruamel.yaml.parser.Parser if pure or CParser is _A else CParser;self.Composer=ruamel.yaml.composer.Composer;self.Constructor=ruamel.yaml.constructor.SafeConstructor
		elif'base'in self.typ:self.Emitter=ruamel.yaml.emitter.Emitter;self.Representer=ruamel.yaml.representer.BaseRepresenter;self.Parser=ruamel.yaml.parser.Parser if pure or CParser is _A else CParser;self.Composer=ruamel.yaml.composer.Composer;self.Constructor=ruamel.yaml.constructor.BaseConstructor
		elif'unsafe'in self.typ:self.Emitter=ruamel.yaml.emitter.Emitter if pure or CEmitter is _A else CEmitter;self.Representer=ruamel.yaml.representer.Representer;self.Parser=ruamel.yaml.parser.Parser if pure or CParser is _A else CParser;self.Composer=ruamel.yaml.composer.Composer;self.Constructor=ruamel.yaml.constructor.Constructor
		else:setup_rt=_C;typ_found=0
		if setup_rt:self.default_flow_style=_B;self.Emitter=ruamel.yaml.emitter.Emitter;self.Serializer=ruamel.yaml.serializer.Serializer;self.Representer=ruamel.yaml.representer.RoundTripRepresenter;self.Scanner=ruamel.yaml.scanner.RoundTripScanner;self.Parser=ruamel.yaml.parser.RoundTripParser;self.Composer=ruamel.yaml.composer.Composer;self.Constructor=ruamel.yaml.constructor.RoundTripConstructor
		del setup_rt;self.stream=_A;self.canonical=_A;self.old_indent=_A;self.width=_A;self.line_break=_A;self.map_indent=_A;self.sequence_indent=_A;self.sequence_dash_offset=0;self.compact_seq_seq=_A;self.compact_seq_map=_A;self.sort_base_mapping_type_on_output=_A;self.top_level_colon_align=_A;self.prefix_colon=_A;self.version=_A;self.preserve_quotes=_A;self.allow_duplicate_keys=_B;self.encoding='utf-8';self.explicit_start=_A;self.explicit_end=_A;self.tags=_A;self.default_style=_A;self.top_level_block_style_scalar_no_indent_error_1_1=_B;self.scalar_after_indicator=_A;self.brace_single_entry_mapping_in_flow_sequence=_B
		for module in self.plug_ins:
			if getattr(module,'typ',_A)in self.typ:typ_found+=1;module.init_typ(self);break
		if typ_found==0:raise NotImplementedError('typ "{}"not recognised (need to install plug-in?)'.format(self.typ))
	@property
	def reader(self):
		try:return self._reader
		except AttributeError:self._reader=self.Reader(_A,loader=self);return self._reader
	@property
	def scanner(self):
		try:return self._scanner
		except AttributeError:self._scanner=self.Scanner(loader=self);return self._scanner
	@property
	def parser(self):
		attr=_D+sys._getframe().f_code.co_name
		if not hasattr(self,attr):
			if self.Parser is not CParser:setattr(self,attr,self.Parser(loader=self))
			elif getattr(self,_I,_A)is _A:return
			else:setattr(self,attr,CParser(self._stream))
		return getattr(self,attr)
	@property
	def composer(self):
		attr=_D+sys._getframe().f_code.co_name
		if not hasattr(self,attr):setattr(self,attr,self.Composer(loader=self))
		return getattr(self,attr)
	@property
	def constructor(self):
		attr=_D+sys._getframe().f_code.co_name
		if not hasattr(self,attr):cnst=self.Constructor(preserve_quotes=self.preserve_quotes,loader=self);cnst.allow_duplicate_keys=self.allow_duplicate_keys;setattr(self,attr,cnst)
		return getattr(self,attr)
	@property
	def resolver(self):
		attr=_D+sys._getframe().f_code.co_name
		if not hasattr(self,attr):setattr(self,attr,self.Resolver(version=self.version,loader=self))
		return getattr(self,attr)
	@property
	def emitter(self):
		attr=_D+sys._getframe().f_code.co_name
		if not hasattr(self,attr):
			if self.Emitter is not CEmitter:
				_emitter=self.Emitter(_A,canonical=self.canonical,indent=self.old_indent,width=self.width,allow_unicode=self.allow_unicode,line_break=self.line_break,prefix_colon=self.prefix_colon,brace_single_entry_mapping_in_flow_sequence=self.brace_single_entry_mapping_in_flow_sequence,dumper=self);setattr(self,attr,_emitter)
				if self.map_indent is not _A:_emitter.best_map_indent=self.map_indent
				if self.sequence_indent is not _A:_emitter.best_sequence_indent=self.sequence_indent
				if self.sequence_dash_offset is not _A:_emitter.sequence_dash_offset=self.sequence_dash_offset
				if self.compact_seq_seq is not _A:_emitter.compact_seq_seq=self.compact_seq_seq
				if self.compact_seq_map is not _A:_emitter.compact_seq_map=self.compact_seq_map
			else:
				if getattr(self,_I,_A)is _A:return
				return
		return getattr(self,attr)
	@property
	def serializer(self):
		attr=_D+sys._getframe().f_code.co_name
		if not hasattr(self,attr):setattr(self,attr,self.Serializer(encoding=self.encoding,explicit_start=self.explicit_start,explicit_end=self.explicit_end,version=self.version,tags=self.tags,dumper=self))
		return getattr(self,attr)
	@property
	def representer(self):
		attr=_D+sys._getframe().f_code.co_name
		if not hasattr(self,attr):
			repres=self.Representer(default_style=self.default_style,default_flow_style=self.default_flow_style,dumper=self)
			if self.sort_base_mapping_type_on_output is not _A:repres.sort_base_mapping_type_on_output=self.sort_base_mapping_type_on_output
			setattr(self,attr,repres)
		return getattr(self,attr)
	def load(self,stream):
		if not hasattr(stream,'read')and hasattr(stream,_F):
			with stream.open('rb')as fp:return self.load(fp)
		constructor,parser=self.get_constructor_parser(stream)
		try:return constructor.get_single_data()
		finally:
			parser.dispose()
			try:self._reader.reset_reader()
			except AttributeError:pass
			try:self._scanner.reset_scanner()
			except AttributeError:pass
	def load_all(self,stream,_kw=enforce):
		if _kw is not enforce:raise TypeError(_H.format(self.__class__.__name__,_kw))
		if not hasattr(stream,'read')and hasattr(stream,_F):
			with stream.open('r')as fp:
				for d in self.load_all(fp,_kw=enforce):yield d
				return
		constructor,parser=self.get_constructor_parser(stream)
		try:
			while constructor.check_data():yield constructor.get_data()
		finally:
			parser.dispose()
			try:self._reader.reset_reader()
			except AttributeError:pass
			try:self._scanner.reset_scanner()
			except AttributeError:pass
	def get_constructor_parser(self,stream):
		if self.Parser is not CParser:
			if self.Reader is _A:self.Reader=ruamel.yaml.reader.Reader
			if self.Scanner is _A:self.Scanner=ruamel.yaml.scanner.Scanner
			self.reader.stream=stream
		elif self.Reader is not _A:
			if self.Scanner is _A:self.Scanner=ruamel.yaml.scanner.Scanner
			self.Parser=ruamel.yaml.parser.Parser;self.reader.stream=stream
		elif self.Scanner is not _A:
			if self.Reader is _A:self.Reader=ruamel.yaml.reader.Reader
			self.Parser=ruamel.yaml.parser.Parser;self.reader.stream=stream
		else:
			rslvr=self.Resolver
			class XLoader(self.Parser,self.Constructor,rslvr):
				def __init__(selfx,stream,version=self.version,preserve_quotes=_A):CParser.__init__(selfx,stream);selfx._parser=selfx._composer=selfx;self.Constructor.__init__(selfx,loader=selfx);selfx.allow_duplicate_keys=self.allow_duplicate_keys;rslvr.__init__(selfx,version=version,loadumper=selfx)
			self._stream=stream;loader=XLoader(stream);return loader,loader
		return self.constructor,self.parser
	def dump(self,data,stream=_A,_kw=enforce,transform=_A):
		if self._context_manager:
			if not self._output:raise TypeError('Missing output stream while dumping from context manager')
			if _kw is not enforce:raise TypeError('{}.dump() takes one positional argument but at least two were given ({!r})'.format(self.__class__.__name__,_kw))
			if transform is not _A:raise TypeError('{}.dump() in the context manager cannot have transform keyword '.format(self.__class__.__name__))
			self._context_manager.dump(data)
		else:
			if stream is _A:raise TypeError('Need a stream argument when not dumping from context manager')
			return self.dump_all([data],stream,_kw,transform=transform)
	def dump_all(self,documents,stream,_kw=enforce,transform=_A):
		if self._context_manager:raise NotImplementedError
		if _kw is not enforce:raise TypeError(_J.format(self.__class__.__name__,_kw))
		self._output=stream;self._context_manager=YAMLContextManager(self,transform=transform)
		for data in documents:self._context_manager.dump(data)
		self._context_manager.teardown_output();self._output=_A;self._context_manager=_A
	def Xdump_all(self,documents,stream,_kw=enforce,transform=_A):
		if not hasattr(stream,'write')and hasattr(stream,_F):
			with stream.open('w')as fp:return self.dump_all(documents,fp,_kw,transform=transform)
		if _kw is not enforce:raise TypeError(_J.format(self.__class__.__name__,_kw))
		if self.top_level_colon_align is _C:tlca=max([len(str(x))for x in documents[0]])
		else:tlca=self.top_level_colon_align
		if transform is not _A:
			fstream=stream
			if self.encoding is _A:stream=StringIO()
			else:stream=BytesIO()
		serializer,representer,emitter=self.get_serializer_representer_emitter(stream,tlca)
		try:
			self.serializer.open()
			for data in documents:
				try:self.representer.represent(data)
				except AttributeError:raise
			self.serializer.close()
		finally:
			try:self.emitter.dispose()
			except AttributeError:raise
			delattr(self,_K);delattr(self,_L)
		if transform:
			val=stream.getvalue()
			if self.encoding:val=val.decode(self.encoding)
			if fstream is _A:transform(val)
			else:fstream.write(transform(val))
	def get_serializer_representer_emitter(self,stream,tlca):
		if self.Emitter is not CEmitter:
			if self.Serializer is _A:self.Serializer=ruamel.yaml.serializer.Serializer
			self.emitter.stream=stream;self.emitter.top_level_colon_align=tlca
			if self.scalar_after_indicator is not _A:self.emitter.scalar_after_indicator=self.scalar_after_indicator
			return self.serializer,self.representer,self.emitter
		if self.Serializer is not _A:
			self.Emitter=ruamel.yaml.emitter.Emitter;self.emitter.stream=stream;self.emitter.top_level_colon_align=tlca
			if self.scalar_after_indicator is not _A:self.emitter.scalar_after_indicator=self.scalar_after_indicator
			return self.serializer,self.representer,self.emitter
		rslvr=ruamel.yaml.resolver.BaseResolver if'base'in self.typ else ruamel.yaml.resolver.Resolver
		class XDumper(CEmitter,self.Representer,rslvr):
			def __init__(selfx,stream,default_style=_A,default_flow_style=_A,canonical=_A,indent=_A,width=_A,allow_unicode=_A,line_break=_A,encoding=_A,explicit_start=_A,explicit_end=_A,version=_A,tags=_A,block_seq_indent=_A,top_level_colon_align=_A,prefix_colon=_A):CEmitter.__init__(selfx,stream,canonical=canonical,indent=indent,width=width,encoding=encoding,allow_unicode=allow_unicode,line_break=line_break,explicit_start=explicit_start,explicit_end=explicit_end,version=version,tags=tags);selfx._emitter=selfx._serializer=selfx._representer=selfx;self.Representer.__init__(selfx,default_style=default_style,default_flow_style=default_flow_style);rslvr.__init__(selfx)
		self._stream=stream;dumper=XDumper(stream,default_style=self.default_style,default_flow_style=self.default_flow_style,canonical=self.canonical,indent=self.old_indent,width=self.width,allow_unicode=self.allow_unicode,line_break=self.line_break,explicit_start=self.explicit_start,explicit_end=self.explicit_end,version=self.version,tags=self.tags);self._emitter=self._serializer=dumper;return dumper,dumper,dumper
	def map(self,**kw):
		if _E in self.typ:from dynaconf.vendor.ruamel.yaml.comments import CommentedMap;return CommentedMap(**kw)
		else:return dict(**kw)
	def seq(self,*args):
		if _E in self.typ:from dynaconf.vendor.ruamel.yaml.comments import CommentedSeq;return CommentedSeq(*args)
		else:return list(*args)
	def official_plug_ins(self):bd=os.path.dirname(__file__);gpbd=os.path.dirname(os.path.dirname(bd));res=[x.replace(gpbd,'')[1:-3]for x in glob.glob(bd+'/*/__plug_in__.py')];return res
	def register_class(self,cls):
		tag=getattr(cls,_G,'!'+cls.__name__)
		try:self.representer.add_representer(cls,cls.to_yaml)
		except AttributeError:
			def t_y(representer,data):return representer.represent_yaml_object(tag,data,cls,flow_style=representer.default_flow_style)
			self.representer.add_representer(cls,t_y)
		try:self.constructor.add_constructor(tag,cls.from_yaml)
		except AttributeError:
			def f_y(constructor,node):return constructor.construct_yaml_object(node,cls)
			self.constructor.add_constructor(tag,f_y)
		return cls
	def parse(self,stream):
		_,parser=self.get_constructor_parser(stream)
		try:
			while parser.check_event():yield parser.get_event()
		finally:
			parser.dispose()
			try:self._reader.reset_reader()
			except AttributeError:pass
			try:self._scanner.reset_scanner()
			except AttributeError:pass
	def __enter__(self):self._context_manager=YAMLContextManager(self);return self
	def __exit__(self,typ,value,traceback):
		if typ:nprint('typ',typ)
		self._context_manager.teardown_output();self._context_manager=_A
	def _indent(self,mapping=_A,sequence=_A,offset=_A):
		if mapping is not _A:self.map_indent=mapping
		if sequence is not _A:self.sequence_indent=sequence
		if offset is not _A:self.sequence_dash_offset=offset
	@property
	def indent(self):return self._indent
	@indent.setter
	def indent(self,val):self.old_indent=val
	@property
	def block_seq_indent(self):return self.sequence_dash_offset
	@block_seq_indent.setter
	def block_seq_indent(self,val):self.sequence_dash_offset=val
	def compact(self,seq_seq=_A,seq_map=_A):self.compact_seq_seq=seq_seq;self.compact_seq_map=seq_map
class YAMLContextManager:
	def __init__(self,yaml,transform=_A):
		self._yaml=yaml;self._output_inited=_B;self._output_path=_A;self._output=self._yaml._output;self._transform=transform
		if not hasattr(self._output,'write')and hasattr(self._output,_F):self._output_path=self._output;self._output=self._output_path.open('w')
		if self._transform is not _A:
			self._fstream=self._output
			if self._yaml.encoding is _A:self._output=StringIO()
			else:self._output=BytesIO()
	def teardown_output(self):
		if self._output_inited:self._yaml.serializer.close()
		else:return
		try:self._yaml.emitter.dispose()
		except AttributeError:raise
		try:delattr(self._yaml,_K);delattr(self._yaml,_L)
		except AttributeError:raise
		if self._transform:
			val=self._output.getvalue()
			if self._yaml.encoding:val=val.decode(self._yaml.encoding)
			if self._fstream is _A:self._transform(val)
			else:self._fstream.write(self._transform(val));self._fstream.flush();self._output=self._fstream
		if self._output_path is not _A:self._output.close()
	def init_output(self,first_data):
		if self._yaml.top_level_colon_align is _C:tlca=max([len(str(x))for x in first_data])
		else:tlca=self._yaml.top_level_colon_align
		self._yaml.get_serializer_representer_emitter(self._output,tlca);self._yaml.serializer.open();self._output_inited=_C
	def dump(self,data):
		if not self._output_inited:self.init_output(data)
		try:self._yaml.representer.represent(data)
		except AttributeError:raise
def yaml_object(yml):
	def yo_deco(cls):
		tag=getattr(cls,_G,'!'+cls.__name__)
		try:yml.representer.add_representer(cls,cls.to_yaml)
		except AttributeError:
			def t_y(representer,data):return representer.represent_yaml_object(tag,data,cls,flow_style=representer.default_flow_style)
			yml.representer.add_representer(cls,t_y)
		try:yml.constructor.add_constructor(tag,cls.from_yaml)
		except AttributeError:
			def f_y(constructor,node):return constructor.construct_yaml_object(node,cls)
			yml.constructor.add_constructor(tag,f_y)
		return cls
	return yo_deco
def scan(stream,Loader=Loader):
	loader=Loader(stream)
	try:
		while loader.scanner.check_token():yield loader.scanner.get_token()
	finally:loader._parser.dispose()
def parse(stream,Loader=Loader):
	loader=Loader(stream)
	try:
		while loader._parser.check_event():yield loader._parser.get_event()
	finally:loader._parser.dispose()
def compose(stream,Loader=Loader):
	loader=Loader(stream)
	try:return loader.get_single_node()
	finally:loader.dispose()
def compose_all(stream,Loader=Loader):
	loader=Loader(stream)
	try:
		while loader.check_node():yield loader._composer.get_node()
	finally:loader._parser.dispose()
def load(stream,Loader=_A,version=_A,preserve_quotes=_A):
	if Loader is _A:warnings.warn(UnsafeLoaderWarning.text,UnsafeLoaderWarning,stacklevel=2);Loader=UnsafeLoader
	loader=Loader(stream,version,preserve_quotes=preserve_quotes)
	try:return loader._constructor.get_single_data()
	finally:
		loader._parser.dispose()
		try:loader._reader.reset_reader()
		except AttributeError:pass
		try:loader._scanner.reset_scanner()
		except AttributeError:pass
def load_all(stream,Loader=_A,version=_A,preserve_quotes=_A):
	if Loader is _A:warnings.warn(UnsafeLoaderWarning.text,UnsafeLoaderWarning,stacklevel=2);Loader=UnsafeLoader
	loader=Loader(stream,version,preserve_quotes=preserve_quotes)
	try:
		while loader._constructor.check_data():yield loader._constructor.get_data()
	finally:
		loader._parser.dispose()
		try:loader._reader.reset_reader()
		except AttributeError:pass
		try:loader._scanner.reset_scanner()
		except AttributeError:pass
def safe_load(stream,version=_A):return load(stream,SafeLoader,version)
def safe_load_all(stream,version=_A):return load_all(stream,SafeLoader,version)
def round_trip_load(stream,version=_A,preserve_quotes=_A):return load(stream,RoundTripLoader,version,preserve_quotes=preserve_quotes)
def round_trip_load_all(stream,version=_A,preserve_quotes=_A):return load_all(stream,RoundTripLoader,version,preserve_quotes=preserve_quotes)
def emit(events,stream=_A,Dumper=Dumper,canonical=_A,indent=_A,width=_A,allow_unicode=_A,line_break=_A):
	getvalue=_A
	if stream is _A:stream=StringIO();getvalue=stream.getvalue
	dumper=Dumper(stream,canonical=canonical,indent=indent,width=width,allow_unicode=allow_unicode,line_break=line_break)
	try:
		for event in events:dumper.emit(event)
	finally:
		try:dumper._emitter.dispose()
		except AttributeError:raise;dumper.dispose()
	if getvalue is not _A:return getvalue()
enc=_A if PY3 else'utf-8'
def serialize_all(nodes,stream=_A,Dumper=Dumper,canonical=_A,indent=_A,width=_A,allow_unicode=_A,line_break=_A,encoding=enc,explicit_start=_A,explicit_end=_A,version=_A,tags=_A):
	getvalue=_A
	if stream is _A:
		if encoding is _A:stream=StringIO()
		else:stream=BytesIO()
		getvalue=stream.getvalue
	dumper=Dumper(stream,canonical=canonical,indent=indent,width=width,allow_unicode=allow_unicode,line_break=line_break,encoding=encoding,version=version,tags=tags,explicit_start=explicit_start,explicit_end=explicit_end)
	try:
		dumper._serializer.open()
		for node in nodes:dumper.serialize(node)
		dumper._serializer.close()
	finally:
		try:dumper._emitter.dispose()
		except AttributeError:raise;dumper.dispose()
	if getvalue is not _A:return getvalue()
def serialize(node,stream=_A,Dumper=Dumper,**kwds):return serialize_all([node],stream,Dumper=Dumper,**kwds)
def dump_all(documents,stream=_A,Dumper=Dumper,default_style=_A,default_flow_style=_A,canonical=_A,indent=_A,width=_A,allow_unicode=_A,line_break=_A,encoding=enc,explicit_start=_A,explicit_end=_A,version=_A,tags=_A,block_seq_indent=_A,top_level_colon_align=_A,prefix_colon=_A):
	getvalue=_A
	if top_level_colon_align is _C:top_level_colon_align=max([len(str(x))for x in documents[0]])
	if stream is _A:
		if encoding is _A:stream=StringIO()
		else:stream=BytesIO()
		getvalue=stream.getvalue
	dumper=Dumper(stream,default_style=default_style,default_flow_style=default_flow_style,canonical=canonical,indent=indent,width=width,allow_unicode=allow_unicode,line_break=line_break,encoding=encoding,explicit_start=explicit_start,explicit_end=explicit_end,version=version,tags=tags,block_seq_indent=block_seq_indent,top_level_colon_align=top_level_colon_align,prefix_colon=prefix_colon)
	try:
		dumper._serializer.open()
		for data in documents:
			try:dumper._representer.represent(data)
			except AttributeError:raise
		dumper._serializer.close()
	finally:
		try:dumper._emitter.dispose()
		except AttributeError:raise;dumper.dispose()
	if getvalue is not _A:return getvalue()
def dump(data,stream=_A,Dumper=Dumper,default_style=_A,default_flow_style=_A,canonical=_A,indent=_A,width=_A,allow_unicode=_A,line_break=_A,encoding=enc,explicit_start=_A,explicit_end=_A,version=_A,tags=_A,block_seq_indent=_A):return dump_all([data],stream,Dumper=Dumper,default_style=default_style,default_flow_style=default_flow_style,canonical=canonical,indent=indent,width=width,allow_unicode=allow_unicode,line_break=line_break,encoding=encoding,explicit_start=explicit_start,explicit_end=explicit_end,version=version,tags=tags,block_seq_indent=block_seq_indent)
def safe_dump_all(documents,stream=_A,**kwds):return dump_all(documents,stream,Dumper=SafeDumper,**kwds)
def safe_dump(data,stream=_A,**kwds):return dump_all([data],stream,Dumper=SafeDumper,**kwds)
def round_trip_dump(data,stream=_A,Dumper=RoundTripDumper,default_style=_A,default_flow_style=_A,canonical=_A,indent=_A,width=_A,allow_unicode=_A,line_break=_A,encoding=enc,explicit_start=_A,explicit_end=_A,version=_A,tags=_A,block_seq_indent=_A,top_level_colon_align=_A,prefix_colon=_A):allow_unicode=_C if allow_unicode is _A else allow_unicode;return dump_all([data],stream,Dumper=Dumper,default_style=default_style,default_flow_style=default_flow_style,canonical=canonical,indent=indent,width=width,allow_unicode=allow_unicode,line_break=line_break,encoding=encoding,explicit_start=explicit_start,explicit_end=explicit_end,version=version,tags=tags,block_seq_indent=block_seq_indent,top_level_colon_align=top_level_colon_align,prefix_colon=prefix_colon)
def add_implicit_resolver(tag,regexp,first=_A,Loader=_A,Dumper=_A,resolver=Resolver):
	A='add_implicit_resolver'
	if Loader is _A and Dumper is _A:resolver.add_implicit_resolver(tag,regexp,first);return
	if Loader:
		if hasattr(Loader,A):Loader.add_implicit_resolver(tag,regexp,first)
		elif issubclass(Loader,(BaseLoader,SafeLoader,ruamel.yaml.loader.Loader,RoundTripLoader)):Resolver.add_implicit_resolver(tag,regexp,first)
		else:raise NotImplementedError
	if Dumper:
		if hasattr(Dumper,A):Dumper.add_implicit_resolver(tag,regexp,first)
		elif issubclass(Dumper,(BaseDumper,SafeDumper,ruamel.yaml.dumper.Dumper,RoundTripDumper)):Resolver.add_implicit_resolver(tag,regexp,first)
		else:raise NotImplementedError
def add_path_resolver(tag,path,kind=_A,Loader=_A,Dumper=_A,resolver=Resolver):
	A='add_path_resolver'
	if Loader is _A and Dumper is _A:resolver.add_path_resolver(tag,path,kind);return
	if Loader:
		if hasattr(Loader,A):Loader.add_path_resolver(tag,path,kind)
		elif issubclass(Loader,(BaseLoader,SafeLoader,ruamel.yaml.loader.Loader,RoundTripLoader)):Resolver.add_path_resolver(tag,path,kind)
		else:raise NotImplementedError
	if Dumper:
		if hasattr(Dumper,A):Dumper.add_path_resolver(tag,path,kind)
		elif issubclass(Dumper,(BaseDumper,SafeDumper,ruamel.yaml.dumper.Dumper,RoundTripDumper)):Resolver.add_path_resolver(tag,path,kind)
		else:raise NotImplementedError
def add_constructor(tag,object_constructor,Loader=_A,constructor=Constructor):
	if Loader is _A:constructor.add_constructor(tag,object_constructor)
	else:
		if hasattr(Loader,'add_constructor'):Loader.add_constructor(tag,object_constructor);return
		if issubclass(Loader,BaseLoader):BaseConstructor.add_constructor(tag,object_constructor)
		elif issubclass(Loader,SafeLoader):SafeConstructor.add_constructor(tag,object_constructor)
		elif issubclass(Loader,Loader):Constructor.add_constructor(tag,object_constructor)
		elif issubclass(Loader,RoundTripLoader):RoundTripConstructor.add_constructor(tag,object_constructor)
		else:raise NotImplementedError
def add_multi_constructor(tag_prefix,multi_constructor,Loader=_A,constructor=Constructor):
	if Loader is _A:constructor.add_multi_constructor(tag_prefix,multi_constructor)
	else:
		if _B and hasattr(Loader,'add_multi_constructor'):Loader.add_multi_constructor(tag_prefix,constructor);return
		if issubclass(Loader,BaseLoader):BaseConstructor.add_multi_constructor(tag_prefix,multi_constructor)
		elif issubclass(Loader,SafeLoader):SafeConstructor.add_multi_constructor(tag_prefix,multi_constructor)
		elif issubclass(Loader,ruamel.yaml.loader.Loader):Constructor.add_multi_constructor(tag_prefix,multi_constructor)
		elif issubclass(Loader,RoundTripLoader):RoundTripConstructor.add_multi_constructor(tag_prefix,multi_constructor)
		else:raise NotImplementedError
def add_representer(data_type,object_representer,Dumper=_A,representer=Representer):
	if Dumper is _A:representer.add_representer(data_type,object_representer)
	else:
		if hasattr(Dumper,'add_representer'):Dumper.add_representer(data_type,object_representer);return
		if issubclass(Dumper,BaseDumper):BaseRepresenter.add_representer(data_type,object_representer)
		elif issubclass(Dumper,SafeDumper):SafeRepresenter.add_representer(data_type,object_representer)
		elif issubclass(Dumper,Dumper):Representer.add_representer(data_type,object_representer)
		elif issubclass(Dumper,RoundTripDumper):RoundTripRepresenter.add_representer(data_type,object_representer)
		else:raise NotImplementedError
def add_multi_representer(data_type,multi_representer,Dumper=_A,representer=Representer):
	if Dumper is _A:representer.add_multi_representer(data_type,multi_representer)
	else:
		if hasattr(Dumper,'add_multi_representer'):Dumper.add_multi_representer(data_type,multi_representer);return
		if issubclass(Dumper,BaseDumper):BaseRepresenter.add_multi_representer(data_type,multi_representer)
		elif issubclass(Dumper,SafeDumper):SafeRepresenter.add_multi_representer(data_type,multi_representer)
		elif issubclass(Dumper,Dumper):Representer.add_multi_representer(data_type,multi_representer)
		elif issubclass(Dumper,RoundTripDumper):RoundTripRepresenter.add_multi_representer(data_type,multi_representer)
		else:raise NotImplementedError
class YAMLObjectMetaclass(type):
	def __init__(cls,name,bases,kwds):
		super(YAMLObjectMetaclass,cls).__init__(name,bases,kwds)
		if _G in kwds and kwds[_G]is not _A:cls.yaml_constructor.add_constructor(cls.yaml_tag,cls.from_yaml);cls.yaml_representer.add_representer(cls,cls.to_yaml)
class YAMLObject(with_metaclass(YAMLObjectMetaclass)):
	__slots__=();yaml_constructor=Constructor;yaml_representer=Representer;yaml_tag=_A;yaml_flow_style=_A
	@classmethod
	def from_yaml(cls,constructor,node):return constructor.construct_yaml_object(node,cls)
	@classmethod
	def to_yaml(cls,representer,data):return representer.represent_yaml_object(cls.yaml_tag,data,cls,flow_style=cls.yaml_flow_style)
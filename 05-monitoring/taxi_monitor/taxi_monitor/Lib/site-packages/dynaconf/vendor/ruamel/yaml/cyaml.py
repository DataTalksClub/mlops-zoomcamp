from __future__ import absolute_import
_A=None
from _ruamel_yaml import CParser,CEmitter
from.constructor import Constructor,BaseConstructor,SafeConstructor
from.representer import Representer,SafeRepresenter,BaseRepresenter
from.resolver import Resolver,BaseResolver
if False:from typing import Any,Union,Optional;from.compat import StreamTextType,StreamType,VersionType
__all__=['CBaseLoader','CSafeLoader','CLoader','CBaseDumper','CSafeDumper','CDumper']
class CBaseLoader(CParser,BaseConstructor,BaseResolver):
	def __init__(A,stream,version=_A,preserve_quotes=_A):CParser.__init__(A,stream);A._parser=A._composer=A;BaseConstructor.__init__(A,loader=A);BaseResolver.__init__(A,loadumper=A)
class CSafeLoader(CParser,SafeConstructor,Resolver):
	def __init__(A,stream,version=_A,preserve_quotes=_A):CParser.__init__(A,stream);A._parser=A._composer=A;SafeConstructor.__init__(A,loader=A);Resolver.__init__(A,loadumper=A)
class CLoader(CParser,Constructor,Resolver):
	def __init__(A,stream,version=_A,preserve_quotes=_A):CParser.__init__(A,stream);A._parser=A._composer=A;Constructor.__init__(A,loader=A);Resolver.__init__(A,loadumper=A)
class CBaseDumper(CEmitter,BaseRepresenter,BaseResolver):
	def __init__(A,stream,default_style=_A,default_flow_style=_A,canonical=_A,indent=_A,width=_A,allow_unicode=_A,line_break=_A,encoding=_A,explicit_start=_A,explicit_end=_A,version=_A,tags=_A,block_seq_indent=_A,top_level_colon_align=_A,prefix_colon=_A):CEmitter.__init__(A,stream,canonical=canonical,indent=indent,width=width,encoding=encoding,allow_unicode=allow_unicode,line_break=line_break,explicit_start=explicit_start,explicit_end=explicit_end,version=version,tags=tags);A._emitter=A._serializer=A._representer=A;BaseRepresenter.__init__(A,default_style=default_style,default_flow_style=default_flow_style,dumper=A);BaseResolver.__init__(A,loadumper=A)
class CSafeDumper(CEmitter,SafeRepresenter,Resolver):
	def __init__(A,stream,default_style=_A,default_flow_style=_A,canonical=_A,indent=_A,width=_A,allow_unicode=_A,line_break=_A,encoding=_A,explicit_start=_A,explicit_end=_A,version=_A,tags=_A,block_seq_indent=_A,top_level_colon_align=_A,prefix_colon=_A):A._emitter=A._serializer=A._representer=A;CEmitter.__init__(A,stream,canonical=canonical,indent=indent,width=width,encoding=encoding,allow_unicode=allow_unicode,line_break=line_break,explicit_start=explicit_start,explicit_end=explicit_end,version=version,tags=tags);A._emitter=A._serializer=A._representer=A;SafeRepresenter.__init__(A,default_style=default_style,default_flow_style=default_flow_style);Resolver.__init__(A)
class CDumper(CEmitter,Representer,Resolver):
	def __init__(A,stream,default_style=_A,default_flow_style=_A,canonical=_A,indent=_A,width=_A,allow_unicode=_A,line_break=_A,encoding=_A,explicit_start=_A,explicit_end=_A,version=_A,tags=_A,block_seq_indent=_A,top_level_colon_align=_A,prefix_colon=_A):CEmitter.__init__(A,stream,canonical=canonical,indent=indent,width=width,encoding=encoding,allow_unicode=allow_unicode,line_break=line_break,explicit_start=explicit_start,explicit_end=explicit_end,version=version,tags=tags);A._emitter=A._serializer=A._representer=A;Representer.__init__(A,default_style=default_style,default_flow_style=default_flow_style);Resolver.__init__(A)
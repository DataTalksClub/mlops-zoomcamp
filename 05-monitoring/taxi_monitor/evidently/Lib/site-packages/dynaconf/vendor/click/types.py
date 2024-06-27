_E='replace'
_D='utf-8'
_C=True
_B=False
_A=None
import os,stat
from datetime import datetime
from._compat import _get_argv_encoding
from._compat import filename_to_ui
from._compat import get_filesystem_encoding
from._compat import get_strerror
from._compat import open_stream
from.exceptions import BadParameter
from.utils import LazyFile
from.utils import safecall
class ParamType:
	is_composite=_B;name=_A;envvar_list_splitter=_A
	def __call__(B,value,param=_A,ctx=_A):
		A=value
		if A is not _A:return B.convert(A,param,ctx)
	def get_metavar(A,param):0
	def get_missing_message(A,param):0
	def convert(A,value,param,ctx):return value
	def split_envvar_value(A,rv):return(rv or'').split(A.envvar_list_splitter)
	def fail(A,message,param=_A,ctx=_A):raise BadParameter(message,ctx=ctx,param=param)
class CompositeParamType(ParamType):
	is_composite=_C
	@property
	def arity(self):raise NotImplementedError()
class FuncParamType(ParamType):
	def __init__(A,func):A.name=func.__name__;A.func=func
	def convert(B,value,param,ctx):
		A=value
		try:return B.func(A)
		except ValueError:
			try:A=str(A)
			except UnicodeError:A=A.decode(_D,_E)
			B.fail(A,param,ctx)
class UnprocessedParamType(ParamType):
	name='text'
	def convert(A,value,param,ctx):return value
	def __repr__(A):return'UNPROCESSED'
class StringParamType(ParamType):
	name='text'
	def convert(D,value,param,ctx):
		A=value
		if isinstance(A,bytes):
			B=_get_argv_encoding()
			try:A=A.decode(B)
			except UnicodeError:
				C=get_filesystem_encoding()
				if C!=B:
					try:A=A.decode(C)
					except UnicodeError:A=A.decode(_D,_E)
				else:A=A.decode(_D,_E)
			return A
		return A
	def __repr__(A):return'STRING'
class Choice(ParamType):
	name='choice'
	def __init__(A,choices,case_sensitive=_C):A.choices=choices;A.case_sensitive=case_sensitive
	def get_metavar(A,param):return f"[{'|'.join(A.choices)}]"
	def get_missing_message(A,param):B=',\n\t'.join(A.choices);return f"Choose from:\n\t{B}"
	def convert(D,value,param,ctx):
		E=value;B=ctx;C=E;A={A:A for A in D.choices}
		if B is not _A and B.token_normalize_func is not _A:C=B.token_normalize_func(E);A={B.token_normalize_func(A):C for(A,C)in A.items()}
		if not D.case_sensitive:C=C.casefold();A={A.casefold():B for(A,B)in A.items()}
		if C in A:return A[C]
		D.fail(f"invalid choice: {E}. (choose from {', '.join(D.choices)})",param,B)
	def __repr__(A):return f"Choice({list(A.choices)})"
class DateTime(ParamType):
	name='datetime'
	def __init__(A,formats=_A):A.formats=formats or['%Y-%m-%d','%Y-%m-%dT%H:%M:%S','%Y-%m-%d %H:%M:%S']
	def get_metavar(A,param):return f"[{'|'.join(A.formats)}]"
	def _try_to_convert_date(A,value,format):
		try:return datetime.strptime(value,format)
		except ValueError:return
	def convert(A,value,param,ctx):
		B=value
		for format in A.formats:
			C=A._try_to_convert_date(B,format)
			if C:return C
		A.fail(f"invalid datetime format: {B}. (choose from {', '.join(A.formats)})")
	def __repr__(A):return'DateTime'
class IntParamType(ParamType):
	name='integer'
	def convert(B,value,param,ctx):
		A=value
		try:return int(A)
		except ValueError:B.fail(f"{A} is not a valid integer",param,ctx)
	def __repr__(A):return'INT'
class IntRange(IntParamType):
	name='integer range'
	def __init__(A,min=_A,max=_A,clamp=_B):A.min=min;A.max=max;A.clamp=clamp
	def convert(A,value,param,ctx):
		D=ctx;C=param;B=IntParamType.convert(A,value,C,D)
		if A.clamp:
			if A.min is not _A and B<A.min:return A.min
			if A.max is not _A and B>A.max:return A.max
		if A.min is not _A and B<A.min or A.max is not _A and B>A.max:
			if A.min is _A:A.fail(f"{B} is bigger than the maximum valid value {A.max}.",C,D)
			elif A.max is _A:A.fail(f"{B} is smaller than the minimum valid value {A.min}.",C,D)
			else:A.fail(f"{B} is not in the valid range of {A.min} to {A.max}.",C,D)
		return B
	def __repr__(A):return f"IntRange({A.min}, {A.max})"
class FloatParamType(ParamType):
	name='float'
	def convert(B,value,param,ctx):
		A=value
		try:return float(A)
		except ValueError:B.fail(f"{A} is not a valid floating point value",param,ctx)
	def __repr__(A):return'FLOAT'
class FloatRange(FloatParamType):
	name='float range'
	def __init__(A,min=_A,max=_A,clamp=_B):A.min=min;A.max=max;A.clamp=clamp
	def convert(A,value,param,ctx):
		D=ctx;C=param;B=FloatParamType.convert(A,value,C,D)
		if A.clamp:
			if A.min is not _A and B<A.min:return A.min
			if A.max is not _A and B>A.max:return A.max
		if A.min is not _A and B<A.min or A.max is not _A and B>A.max:
			if A.min is _A:A.fail(f"{B} is bigger than the maximum valid value {A.max}.",C,D)
			elif A.max is _A:A.fail(f"{B} is smaller than the minimum valid value {A.min}.",C,D)
			else:A.fail(f"{B} is not in the valid range of {A.min} to {A.max}.",C,D)
		return B
	def __repr__(A):return f"FloatRange({A.min}, {A.max})"
class BoolParamType(ParamType):
	name='boolean'
	def convert(B,value,param,ctx):
		A=value
		if isinstance(A,bool):return bool(A)
		A=A.lower()
		if A in('true','t','1','yes','y'):return _C
		elif A in('false','f','0','no','n'):return _B
		B.fail(f"{A} is not a valid boolean",param,ctx)
	def __repr__(A):return'BOOL'
class UUIDParameterType(ParamType):
	name='uuid'
	def convert(B,value,param,ctx):
		A=value;import uuid
		try:return uuid.UUID(A)
		except ValueError:B.fail(f"{A} is not a valid UUID value",param,ctx)
	def __repr__(A):return'UUID'
class File(ParamType):
	name='filename';envvar_list_splitter=os.path.pathsep
	def __init__(A,mode='r',encoding=_A,errors='strict',lazy=_A,atomic=_B):A.mode=mode;A.encoding=encoding;A.errors=errors;A.lazy=lazy;A.atomic=atomic
	def resolve_lazy_flag(A,value):
		if A.lazy is not _A:return A.lazy
		if value=='-':return _B
		elif'w'in A.mode:return _C
		return _B
	def convert(A,value,param,ctx):
		C=ctx;B=value
		try:
			if hasattr(B,'read')or hasattr(B,'write'):return B
			E=A.resolve_lazy_flag(B)
			if E:
				D=LazyFile(B,A.mode,A.encoding,A.errors,atomic=A.atomic)
				if C is not _A:C.call_on_close(D.close_intelligently)
				return D
			D,F=open_stream(B,A.mode,A.encoding,A.errors,atomic=A.atomic)
			if C is not _A:
				if F:C.call_on_close(safecall(D.close))
				else:C.call_on_close(safecall(D.flush))
			return D
		except OSError as G:A.fail(f"Could not open file: {filename_to_ui(B)}: {get_strerror(G)}",param,C)
class Path(ParamType):
	envvar_list_splitter=os.path.pathsep
	def __init__(A,exists=_B,file_okay=_C,dir_okay=_C,writable=_B,readable=_C,resolve_path=_B,allow_dash=_B,path_type=_A):
		A.exists=exists;A.file_okay=file_okay;A.dir_okay=dir_okay;A.writable=writable;A.readable=readable;A.resolve_path=resolve_path;A.allow_dash=allow_dash;A.type=path_type
		if A.file_okay and not A.dir_okay:A.name='file';A.path_type='File'
		elif A.dir_okay and not A.file_okay:A.name='directory';A.path_type='Directory'
		else:A.name='path';A.path_type='Path'
	def coerce_path_result(B,rv):
		A=rv
		if B.type is not _A and not isinstance(A,B.type):
			if B.type is str:A=A.decode(get_filesystem_encoding())
			else:A=A.encode(get_filesystem_encoding())
		return A
	def convert(A,value,param,ctx):
		E=ctx;D=param;B=value;C=B;G=A.file_okay and A.allow_dash and C in(b'-','-')
		if not G:
			if A.resolve_path:C=os.path.realpath(C)
			try:F=os.stat(C)
			except OSError:
				if not A.exists:return A.coerce_path_result(C)
				A.fail(f"{A.path_type} {filename_to_ui(B)!r} does not exist.",D,E)
			if not A.file_okay and stat.S_ISREG(F.st_mode):A.fail(f"{A.path_type} {filename_to_ui(B)!r} is a file.",D,E)
			if not A.dir_okay and stat.S_ISDIR(F.st_mode):A.fail(f"{A.path_type} {filename_to_ui(B)!r} is a directory.",D,E)
			if A.writable and not os.access(B,os.W_OK):A.fail(f"{A.path_type} {filename_to_ui(B)!r} is not writable.",D,E)
			if A.readable and not os.access(B,os.R_OK):A.fail(f"{A.path_type} {filename_to_ui(B)!r} is not readable.",D,E)
		return A.coerce_path_result(C)
class Tuple(CompositeParamType):
	def __init__(A,types):A.types=[convert_type(A)for A in types]
	@property
	def name(self):return f"<{' '.join(A.name for A in self.types)}>"
	@property
	def arity(self):return len(self.types)
	def convert(A,value,param,ctx):
		B=value
		if len(B)!=len(A.types):raise TypeError('It would appear that nargs is set to conflict with the composite type arity.')
		return tuple(A(B,param,ctx)for(A,B)in zip(A.types,B))
def convert_type(ty,default=_A):
	B=default;A=ty;C=_B
	if A is _A and B is not _A:
		if isinstance(B,tuple):A=tuple(map(type,B))
		else:A=type(B)
		C=_C
	if isinstance(A,tuple):return Tuple(A)
	if isinstance(A,ParamType):return A
	if A is str or A is _A:return STRING
	if A is int:return INT
	if A is bool and not C:return BOOL
	if A is float:return FLOAT
	if C:return STRING
	if __debug__:
		try:
			if issubclass(A,ParamType):raise AssertionError(f"Attempted to use an uninstantiated parameter type ({A}).")
		except TypeError:pass
	return FuncParamType(A)
UNPROCESSED=UnprocessedParamType()
STRING=StringParamType()
INT=IntParamType()
FLOAT=FloatParamType()
BOOL=BoolParamType()
UUID=UUIDParameterType()
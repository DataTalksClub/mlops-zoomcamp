_D='strict'
_C=True
_B=False
_A=None
import os,sys
from._compat import _default_text_stderr,_default_text_stdout,_find_binary_writer,auto_wrap_for_ansi,binary_streams,filename_to_ui,get_filesystem_encoding,get_strerror,is_bytes,open_stream,should_strip_ansi,strip_ansi,text_streams,WIN
from.globals import resolve_color_default
echo_native_types=str,bytes,bytearray
def _posixify(name):return'-'.join(name.split()).lower()
def safecall(func):
	def A(*A,**B):
		try:return func(*A,**B)
		except Exception:pass
	return A
def make_str(value):
	A=value
	if isinstance(A,bytes):
		try:return A.decode(get_filesystem_encoding())
		except UnicodeError:return A.decode('utf-8','replace')
	return str(A)
def make_default_short_help(help,max_length=45):
	F=help.split();D=0;A=[];C=_B
	for B in F:
		if B[-1:]=='.':C=_C
		E=1+len(B)if A else len(B)
		if D+E>max_length:A.append('...');C=_C
		else:
			if A:A.append(' ')
			A.append(B)
		if C:break
		D+=E
	return''.join(A)
class LazyFile:
	def __init__(A,filename,mode='r',encoding=_A,errors=_D,atomic=_B):
		E=errors;D=encoding;C=mode;B=filename;A.name=B;A.mode=C;A.encoding=D;A.errors=E;A.atomic=atomic
		if B=='-':A._f,A.should_close=open_stream(B,C,D,E)
		else:
			if'r'in C:open(B,C).close()
			A._f=_A;A.should_close=_C
	def __getattr__(A,name):return getattr(A.open(),name)
	def __repr__(A):
		if A._f is not _A:return repr(A._f)
		return f"<unopened file '{A.name}' {A.mode}>"
	def open(A):
		if A._f is not _A:return A._f
		try:B,A.should_close=open_stream(A.name,A.mode,A.encoding,A.errors,atomic=A.atomic)
		except OSError as C:from.exceptions import FileError as D;raise D(A.name,hint=get_strerror(C))
		A._f=B;return B
	def close(A):
		if A._f is not _A:A._f.close()
	def close_intelligently(A):
		if A.should_close:A.close()
	def __enter__(A):return A
	def __exit__(A,exc_type,exc_value,tb):A.close_intelligently()
	def __iter__(A):A.open();return iter(A._f)
class KeepOpenFile:
	def __init__(A,file):A._file=file
	def __getattr__(A,name):return getattr(A._file,name)
	def __enter__(A):return A
	def __exit__(A,exc_type,exc_value,tb):0
	def __repr__(A):return repr(A._file)
	def __iter__(A):return iter(A._file)
def echo(message=_A,file=_A,nl=_C,err=_B,color=_A):
	C=color;B=file;A=message
	if B is _A:
		if err:B=_default_text_stderr()
		else:B=_default_text_stdout()
	if A is not _A and not isinstance(A,echo_native_types):A=str(A)
	if nl:
		A=A or''
		if isinstance(A,str):A+='\n'
		else:A+=b'\n'
	if A and is_bytes(A):
		D=_find_binary_writer(B)
		if D is not _A:B.flush();D.write(A);D.flush();return
	if A and not is_bytes(A):
		C=resolve_color_default(C)
		if should_strip_ansi(B,C):A=strip_ansi(A)
		elif WIN:
			if auto_wrap_for_ansi is not _A:B=auto_wrap_for_ansi(B)
			elif not C:A=strip_ansi(A)
	if A:B.write(A)
	B.flush()
def get_binary_stream(name):
	A=binary_streams.get(name)
	if A is _A:raise TypeError(f"Unknown standard stream '{name}'")
	return A()
def get_text_stream(name,encoding=_A,errors=_D):
	A=text_streams.get(name)
	if A is _A:raise TypeError(f"Unknown standard stream '{name}'")
	return A(encoding,errors)
def open_file(filename,mode='r',encoding=_A,errors=_D,lazy=_B,atomic=_B):
	E=atomic;D=errors;C=encoding;B=filename
	if lazy:return LazyFile(B,mode,C,D,atomic=E)
	A,F=open_stream(B,mode,C,D,atomic=E)
	if not F:A=KeepOpenFile(A)
	return A
def get_os_args():import warnings as A;A.warn("'get_os_args' is deprecated and will be removed in 8.1. Access 'sys.argv[1:]' directly instead.",DeprecationWarning,stacklevel=2);return sys.argv[1:]
def format_filename(filename,shorten=_B):
	A=filename
	if shorten:A=os.path.basename(A)
	return filename_to_ui(A)
def get_app_dir(app_name,roaming=_C,force_posix=_B):
	A=app_name
	if WIN:
		C='APPDATA'if roaming else'LOCALAPPDATA';B=os.environ.get(C)
		if B is _A:B=os.path.expanduser('~')
		return os.path.join(B,A)
	if force_posix:return os.path.join(os.path.expanduser(f"~/.{_posixify(A)}"))
	if sys.platform=='darwin':return os.path.join(os.path.expanduser('~/Library/Application Support'),A)
	return os.path.join(os.environ.get('XDG_CONFIG_HOME',os.path.expanduser('~/.config')),_posixify(A))
class PacifyFlushWrapper:
	def __init__(A,wrapped):A.wrapped=wrapped
	def flush(A):
		try:A.wrapped.flush()
		except OSError as B:
			import errno
			if B.errno!=errno.EPIPE:raise
	def __getattr__(A,attr):return getattr(A.wrapped,attr)
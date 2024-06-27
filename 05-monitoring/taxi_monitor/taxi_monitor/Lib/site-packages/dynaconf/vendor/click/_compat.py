_I='stderr'
_H='stdout'
_G='buffer'
_F='utf-8'
_E='encoding'
_D='replace'
_C=True
_B=False
_A=None
import codecs,io,os,re,sys
from weakref import WeakKeyDictionary
CYGWIN=sys.platform.startswith('cygwin')
MSYS2=sys.platform.startswith('win')and'GCC'in sys.version
APP_ENGINE='APPENGINE_RUNTIME'in os.environ and'Development/'in os.environ.get('SERVER_SOFTWARE','')
WIN=sys.platform.startswith('win')and not APP_ENGINE and not MSYS2
DEFAULT_COLUMNS=80
auto_wrap_for_ansi=_A
colorama=_A
get_winterm_size=_A
_ansi_re=re.compile('\\033\\[[;?0-9]*[a-zA-Z]')
def get_filesystem_encoding():return sys.getfilesystemencoding()or sys.getdefaultencoding()
def _make_text_stream(stream,encoding,errors,force_readable=_B,force_writable=_B):
	C=stream;B=errors;A=encoding
	if A is _A:A=get_best_encoding(C)
	if B is _A:B=_D
	return _NonClosingTextIOWrapper(C,A,B,line_buffering=_C,force_readable=force_readable,force_writable=force_writable)
def is_ascii_encoding(encoding):
	try:return codecs.lookup(encoding).name=='ascii'
	except LookupError:return _B
def get_best_encoding(stream):
	A=getattr(stream,_E,_A)or sys.getdefaultencoding()
	if is_ascii_encoding(A):return _F
	return A
class _NonClosingTextIOWrapper(io.TextIOWrapper):
	def __init__(B,stream,encoding,errors,force_readable=_B,force_writable=_B,**C):A=stream;B._stream=A=_FixupStream(A,force_readable,force_writable);super().__init__(A,encoding,errors,**C)
	def __del__(A):
		try:A.detach()
		except Exception:pass
	def isatty(A):return A._stream.isatty()
class _FixupStream:
	def __init__(A,stream,force_readable=_B,force_writable=_B):A._stream=stream;A._force_readable=force_readable;A._force_writable=force_writable
	def __getattr__(A,name):return getattr(A._stream,name)
	def read1(A,size):
		B=getattr(A._stream,'read1',_A)
		if B is not _A:return B(size)
		return A._stream.read(size)
	def readable(A):
		if A._force_readable:return _C
		B=getattr(A._stream,'readable',_A)
		if B is not _A:return B()
		try:A._stream.read(0)
		except Exception:return _B
		return _C
	def writable(A):
		if A._force_writable:return _C
		B=getattr(A._stream,'writable',_A)
		if B is not _A:return B()
		try:A._stream.write('')
		except Exception:
			try:A._stream.write(b'')
			except Exception:return _B
		return _C
	def seekable(A):
		B=getattr(A._stream,'seekable',_A)
		if B is not _A:return B()
		try:A._stream.seek(A._stream.tell())
		except Exception:return _B
		return _C
def is_bytes(x):return isinstance(x,(bytes,memoryview,bytearray))
def _is_binary_reader(stream,default=_B):
	try:return isinstance(stream.read(0),bytes)
	except Exception:return default
def _is_binary_writer(stream,default=_B):
	A=stream
	try:A.write(b'')
	except Exception:
		try:A.write('');return _B
		except Exception:pass
		return default
	return _C
def _find_binary_reader(stream):
	A=stream
	if _is_binary_reader(A,_B):return A
	B=getattr(A,_G,_A)
	if B is not _A and _is_binary_reader(B,_C):return B
def _find_binary_writer(stream):
	A=stream
	if _is_binary_writer(A,_B):return A
	B=getattr(A,_G,_A)
	if B is not _A and _is_binary_writer(B,_C):return B
def _stream_is_misconfigured(stream):return is_ascii_encoding(getattr(stream,_E,_A)or'ascii')
def _is_compat_stream_attr(stream,attr,value):A=value;B=getattr(stream,attr,_A);return B==A or A is _A and B is not _A
def _is_compatible_text_stream(stream,encoding,errors):A=stream;return _is_compat_stream_attr(A,_E,encoding)and _is_compat_stream_attr(A,'errors',errors)
def _force_correct_text_stream(text_stream,encoding,errors,is_binary,find_binary,force_readable=_B,force_writable=_B):
	C=encoding;B=errors;A=text_stream
	if is_binary(A,_B):D=A
	else:
		if _is_compatible_text_stream(A,C,B)and not(C is _A and _stream_is_misconfigured(A)):return A
		D=find_binary(A)
		if D is _A:return A
	if B is _A:B=_D
	return _make_text_stream(D,C,B,force_readable=force_readable,force_writable=force_writable)
def _force_correct_text_reader(text_reader,encoding,errors,force_readable=_B):return _force_correct_text_stream(text_reader,encoding,errors,_is_binary_reader,_find_binary_reader,force_readable=force_readable)
def _force_correct_text_writer(text_writer,encoding,errors,force_writable=_B):return _force_correct_text_stream(text_writer,encoding,errors,_is_binary_writer,_find_binary_writer,force_writable=force_writable)
def get_binary_stdin():
	A=_find_binary_reader(sys.stdin)
	if A is _A:raise RuntimeError('Was not able to determine binary stream for sys.stdin.')
	return A
def get_binary_stdout():
	A=_find_binary_writer(sys.stdout)
	if A is _A:raise RuntimeError('Was not able to determine binary stream for sys.stdout.')
	return A
def get_binary_stderr():
	A=_find_binary_writer(sys.stderr)
	if A is _A:raise RuntimeError('Was not able to determine binary stream for sys.stderr.')
	return A
def get_text_stdin(encoding=_A,errors=_A):
	B=errors;A=encoding;C=_get_windows_console_stream(sys.stdin,A,B)
	if C is not _A:return C
	return _force_correct_text_reader(sys.stdin,A,B,force_readable=_C)
def get_text_stdout(encoding=_A,errors=_A):
	B=errors;A=encoding;C=_get_windows_console_stream(sys.stdout,A,B)
	if C is not _A:return C
	return _force_correct_text_writer(sys.stdout,A,B,force_writable=_C)
def get_text_stderr(encoding=_A,errors=_A):
	B=errors;A=encoding;C=_get_windows_console_stream(sys.stderr,A,B)
	if C is not _A:return C
	return _force_correct_text_writer(sys.stderr,A,B,force_writable=_C)
def filename_to_ui(value):
	A=value
	if isinstance(A,bytes):A=A.decode(get_filesystem_encoding(),_D)
	else:A=A.encode(_F,'surrogateescape').decode(_F,_D)
	return A
def get_strerror(e,default=_A):
	B=default
	if hasattr(e,'strerror'):A=e.strerror
	elif B is not _A:A=B
	else:A=str(e)
	if isinstance(A,bytes):A=A.decode(_F,_D)
	return A
def _wrap_io_open(file,mode,encoding,errors):
	A=mode
	if'b'in A:return open(file,A)
	return open(file,A,encoding=encoding,errors=errors)
def open_stream(filename,mode='r',encoding=_A,errors='strict',atomic=_B):
	E=errors;D=encoding;B=filename;A=mode;G='b'in A
	if B=='-':
		if any(B in A for B in['w','a','x']):
			if G:return get_binary_stdout(),_B
			return get_text_stdout(encoding=D,errors=E),_B
		if G:return get_binary_stdin(),_B
		return get_text_stdin(encoding=D,errors=E),_B
	if not atomic:return _wrap_io_open(B,A,D,E),_C
	if'a'in A:raise ValueError("Appending to an existing file is not supported, because that would involve an expensive `copy`-operation to a temporary file. Open the file in normal `w`-mode and copy explicitly if that's what you're after.")
	if'x'in A:raise ValueError('Use the `overwrite`-parameter instead.')
	if'w'not in A:raise ValueError('Atomic writes only make sense with `w`-mode.')
	import errno as I,random as K
	try:C=os.stat(B).st_mode
	except OSError:C=_A
	J=os.O_RDWR|os.O_CREAT|os.O_EXCL
	if G:J|=getattr(os,'O_BINARY',0)
	while _C:
		H=os.path.join(os.path.dirname(B),f".__atomic-write{K.randrange(1<<32):08x}")
		try:L=os.open(H,J,438 if C is _A else C);break
		except OSError as F:
			if F.errno==I.EEXIST or os.name=='nt'and F.errno==I.EACCES and os.path.isdir(F.filename)and os.access(F.filename,os.W_OK):continue
			raise
	if C is not _A:os.chmod(H,C)
	M=_wrap_io_open(L,A,D,E);return _AtomicFile(M,H,os.path.realpath(B)),_C
class _AtomicFile:
	def __init__(A,f,tmp_filename,real_filename):A._f=f;A._tmp_filename=tmp_filename;A._real_filename=real_filename;A.closed=_B
	@property
	def name(self):return self._real_filename
	def close(A,delete=_B):
		if A.closed:return
		A._f.close();os.replace(A._tmp_filename,A._real_filename);A.closed=_C
	def __getattr__(A,name):return getattr(A._f,name)
	def __enter__(A):return A
	def __exit__(A,exc_type,exc_value,tb):A.close(delete=exc_type is not _A)
	def __repr__(A):return repr(A._f)
def strip_ansi(value):return _ansi_re.sub('',value)
def _is_jupyter_kernel_output(stream):
	A=stream
	if WIN:return
	while isinstance(A,(_FixupStream,_NonClosingTextIOWrapper)):A=A._stream
	return A.__class__.__module__.startswith('ipykernel.')
def should_strip_ansi(stream=_A,color=_A):
	B=color;A=stream
	if B is _A:
		if A is _A:A=sys.stdin
		return not isatty(A)and not _is_jupyter_kernel_output(A)
	return not B
if WIN:
	DEFAULT_COLUMNS=79;from._winconsole import _get_windows_console_stream
	def _get_argv_encoding():import locale as A;return A.getpreferredencoding()
	try:import colorama
	except ImportError:pass
	else:
		_ansi_stream_wrappers=WeakKeyDictionary()
		def auto_wrap_for_ansi(stream,color=_A):
			A=stream
			try:C=_ansi_stream_wrappers.get(A)
			except Exception:C=_A
			if C is not _A:return C
			E=should_strip_ansi(A,color);D=colorama.AnsiToWin32(A,strip=E);B=D.stream;F=B.write
			def G(s):
				try:return F(s)
				except BaseException:D.reset_all();raise
			B.write=G
			try:_ansi_stream_wrappers[A]=B
			except Exception:pass
			return B
		def get_winterm_size():A=colorama.win32.GetConsoleScreenBufferInfo(colorama.win32.STDOUT).srWindow;return A.Right-A.Left,A.Bottom-A.Top
else:
	def _get_argv_encoding():return getattr(sys.stdin,_E,_A)or get_filesystem_encoding()
	def _get_windows_console_stream(f,encoding,errors):0
def term_len(x):return len(strip_ansi(x))
def isatty(stream):
	try:return stream.isatty()
	except Exception:return _B
def _make_cached_stream_func(src_func,wrapper_func):
	C=src_func;D=WeakKeyDictionary()
	def A():
		B=C()
		try:A=D.get(B)
		except Exception:A=_A
		if A is not _A:return A
		A=wrapper_func()
		try:B=C();D[B]=A
		except Exception:pass
		return A
	return A
_default_text_stdin=_make_cached_stream_func(lambda:sys.stdin,get_text_stdin)
_default_text_stdout=_make_cached_stream_func(lambda:sys.stdout,get_text_stdout)
_default_text_stderr=_make_cached_stream_func(lambda:sys.stderr,get_text_stderr)
binary_streams={'stdin':get_binary_stdin,_H:get_binary_stdout,_I:get_binary_stderr}
text_streams={'stdin':get_text_stdin,_H:get_text_stdout,_I:get_text_stderr}
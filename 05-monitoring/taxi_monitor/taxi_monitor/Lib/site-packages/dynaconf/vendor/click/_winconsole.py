_E=False
_D='strict'
_C='utf-16-le'
_B=True
_A=None
import ctypes,io,time
from ctypes import byref,c_char,c_char_p,c_int,c_ssize_t,c_ulong,c_void_p,POINTER,py_object,windll,WINFUNCTYPE
from ctypes.wintypes import DWORD
from ctypes.wintypes import HANDLE
from ctypes.wintypes import LPCWSTR
from ctypes.wintypes import LPWSTR
import msvcrt
from._compat import _NonClosingTextIOWrapper
try:from ctypes import pythonapi
except ImportError:pythonapi=_A
else:PyObject_GetBuffer=pythonapi.PyObject_GetBuffer;PyBuffer_Release=pythonapi.PyBuffer_Release
c_ssize_p=POINTER(c_ssize_t)
kernel32=windll.kernel32
GetStdHandle=kernel32.GetStdHandle
ReadConsoleW=kernel32.ReadConsoleW
WriteConsoleW=kernel32.WriteConsoleW
GetConsoleMode=kernel32.GetConsoleMode
GetLastError=kernel32.GetLastError
GetCommandLineW=WINFUNCTYPE(LPWSTR)(('GetCommandLineW',windll.kernel32))
CommandLineToArgvW=WINFUNCTYPE(POINTER(LPWSTR),LPCWSTR,POINTER(c_int))(('CommandLineToArgvW',windll.shell32))
LocalFree=WINFUNCTYPE(ctypes.c_void_p,ctypes.c_void_p)(('LocalFree',windll.kernel32))
STDIN_HANDLE=GetStdHandle(-10)
STDOUT_HANDLE=GetStdHandle(-11)
STDERR_HANDLE=GetStdHandle(-12)
PyBUF_SIMPLE=0
PyBUF_WRITABLE=1
ERROR_SUCCESS=0
ERROR_NOT_ENOUGH_MEMORY=8
ERROR_OPERATION_ABORTED=995
STDIN_FILENO=0
STDOUT_FILENO=1
STDERR_FILENO=2
EOF=b'\x1a'
MAX_BYTES_WRITTEN=32767
class Py_buffer(ctypes.Structure):_fields_=[('buf',c_void_p),('obj',py_object),('len',c_ssize_t),('itemsize',c_ssize_t),('readonly',c_int),('ndim',c_int),('format',c_char_p),('shape',c_ssize_p),('strides',c_ssize_p),('suboffsets',c_ssize_p),('internal',c_void_p)]
if pythonapi is _A:get_buffer=_A
else:
	def get_buffer(obj,writable=_E):
		A=Py_buffer();B=PyBUF_WRITABLE if writable else PyBUF_SIMPLE;PyObject_GetBuffer(py_object(obj),byref(A),B)
		try:C=c_char*A.len;return C.from_address(A.buf)
		finally:PyBuffer_Release(byref(A))
class _WindowsConsoleRawIOBase(io.RawIOBase):
	def __init__(A,handle):A.handle=handle
	def isatty(A):io.RawIOBase.isatty(A);return _B
class _WindowsConsoleReader(_WindowsConsoleRawIOBase):
	def readable(A):return _B
	def readinto(D,b):
		A=len(b)
		if not A:return 0
		elif A%2:raise ValueError('cannot read odd number of bytes from UTF-16-LE encoded console')
		B=get_buffer(b,writable=_B);E=A//2;C=c_ulong();F=ReadConsoleW(HANDLE(D.handle),B,E,byref(C),_A)
		if GetLastError()==ERROR_OPERATION_ABORTED:time.sleep(.1)
		if not F:raise OSError(f"Windows error: {GetLastError()}")
		if B[0]==EOF:return 0
		return 2*C.value
class _WindowsConsoleWriter(_WindowsConsoleRawIOBase):
	def writable(A):return _B
	@staticmethod
	def _get_error_message(errno):
		A=errno
		if A==ERROR_SUCCESS:return'ERROR_SUCCESS'
		elif A==ERROR_NOT_ENOUGH_MEMORY:return'ERROR_NOT_ENOUGH_MEMORY'
		return f"Windows error {A}"
	def write(A,b):
		B=len(b);E=get_buffer(b);F=min(B,MAX_BYTES_WRITTEN)//2;C=c_ulong();WriteConsoleW(HANDLE(A.handle),E,F,byref(C),_A);D=2*C.value
		if D==0 and B>0:raise OSError(A._get_error_message(GetLastError()))
		return D
class ConsoleStream:
	def __init__(A,text_stream,byte_stream):A._text_stream=text_stream;A.buffer=byte_stream
	@property
	def name(self):return self.buffer.name
	def write(A,x):
		if isinstance(x,str):return A._text_stream.write(x)
		try:A.flush()
		except Exception:pass
		return A.buffer.write(x)
	def writelines(A,lines):
		for B in lines:A.write(B)
	def __getattr__(A,name):return getattr(A._text_stream,name)
	def isatty(A):return A.buffer.isatty()
	def __repr__(A):return f"<ConsoleStream name={A.name!r} encoding={A.encoding!r}>"
class WindowsChunkedWriter:
	def __init__(A,wrapped):A.__wrapped=wrapped
	def __getattr__(A,name):return getattr(A.__wrapped,name)
	def write(D,text):
		B=len(text);A=0
		while A<B:C=min(B-A,MAX_BYTES_WRITTEN);D.__wrapped.write(text[A:A+C]);A+=C
def _get_text_stdin(buffer_stream):A=_NonClosingTextIOWrapper(io.BufferedReader(_WindowsConsoleReader(STDIN_HANDLE)),_C,_D,line_buffering=_B);return ConsoleStream(A,buffer_stream)
def _get_text_stdout(buffer_stream):A=_NonClosingTextIOWrapper(io.BufferedWriter(_WindowsConsoleWriter(STDOUT_HANDLE)),_C,_D,line_buffering=_B);return ConsoleStream(A,buffer_stream)
def _get_text_stderr(buffer_stream):A=_NonClosingTextIOWrapper(io.BufferedWriter(_WindowsConsoleWriter(STDERR_HANDLE)),_C,_D,line_buffering=_B);return ConsoleStream(A,buffer_stream)
_stream_factories={0:_get_text_stdin,1:_get_text_stdout,2:_get_text_stderr}
def _is_console(f):
	if not hasattr(f,'fileno'):return _E
	try:A=f.fileno()
	except OSError:return _E
	B=msvcrt.get_osfhandle(A);return bool(GetConsoleMode(B,byref(DWORD())))
def _get_windows_console_stream(f,encoding,errors):
	if get_buffer is not _A and encoding in{_C,_A}and errors in{_D,_A}and _is_console(f):
		A=_stream_factories.get(f.fileno())
		if A is not _A:
			f=getattr(f,'buffer',_A)
			if f is _A:return
			return A(f)
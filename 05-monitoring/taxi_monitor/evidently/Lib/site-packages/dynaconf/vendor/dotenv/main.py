from __future__ import absolute_import,print_function,unicode_literals
_D='always'
_C=True
_B=False
_A=None
import io,logging,os,re,shutil,sys,tempfile
from collections import OrderedDict
from contextlib import contextmanager
from.compat import IS_TYPE_CHECKING,PY2,StringIO,to_env
from.parser import Binding,parse_stream
logger=logging.getLogger(__name__)
if IS_TYPE_CHECKING:
	from typing import Dict,Iterator,Match,Optional,Pattern,Union,Text,IO,Tuple
	if sys.version_info>=(3,6):_PathLike=os.PathLike
	else:_PathLike=Text
	if sys.version_info>=(3,0):_StringIO=StringIO
	else:_StringIO=StringIO[Text]
__posix_variable=re.compile('\n    \\$\\{\n        (?P<name>[^\\}:]*)\n        (?::-\n            (?P<default>[^\\}]*)\n        )?\n    \\}\n    ',re.VERBOSE)
def with_warn_for_invalid_lines(mappings):
	for A in mappings:
		if A.error:logger.warning('Python-dotenv could not parse statement starting at line %s',A.original.line)
		yield A
class DotEnv:
	def __init__(A,dotenv_path,verbose=_B,encoding=_A,interpolate=_C):A.dotenv_path=dotenv_path;A._dict=_A;A.verbose=verbose;A.encoding=encoding;A.interpolate=interpolate
	@contextmanager
	def _get_stream(self):
		A=self
		if isinstance(A.dotenv_path,StringIO):yield A.dotenv_path
		elif os.path.isfile(A.dotenv_path):
			with io.open(A.dotenv_path,encoding=A.encoding)as B:yield B
		else:
			if A.verbose:logger.info('Python-dotenv could not find configuration file %s.',A.dotenv_path or'.env')
			yield StringIO('')
	def dict(A):
		if A._dict:return A._dict
		B=OrderedDict(A.parse());A._dict=resolve_nested_variables(B)if A.interpolate else B;return A._dict
	def parse(B):
		with B._get_stream()as C:
			for A in with_warn_for_invalid_lines(parse_stream(C)):
				if A.key is not _A:yield(A.key,A.value)
	def set_as_environment_variables(C,override=_B):
		for(A,B)in C.dict().items():
			if A in os.environ and not override:continue
			if B is not _A:os.environ[to_env(A)]=to_env(B)
		return _C
	def get(A,key):
		B=key;C=A.dict()
		if B in C:return C[B]
		if A.verbose:logger.warning('Key %s not found in %s.',B,A.dotenv_path)
def get_key(dotenv_path,key_to_get):return DotEnv(dotenv_path,verbose=_C).get(key_to_get)
@contextmanager
def rewrite(path):
	try:
		with tempfile.NamedTemporaryFile(mode='w+',delete=_B)as A:
			with io.open(path)as B:yield(B,A)
	except BaseException:
		if os.path.isfile(A.name):os.unlink(A.name)
		raise
	else:shutil.move(A.name,path)
def set_key(dotenv_path,key_to_set,value_to_set,quote_mode=_D):
	E=quote_mode;C=dotenv_path;B=key_to_set;A=value_to_set;A=A.strip("'").strip('"')
	if not os.path.exists(C):logger.warning("Can't write to %s - it doesn't exist.",C);return _A,B,A
	if' 'in A:E=_D
	if E==_D:F='"{}"'.format(A.replace('"','\\"'))
	else:F=A
	G='{}={}\n'.format(B,F)
	with rewrite(C)as(J,D):
		H=_B
		for I in with_warn_for_invalid_lines(parse_stream(J)):
			if I.key==B:D.write(G);H=_C
			else:D.write(I.original.string)
		if not H:D.write(G)
	return _C,B,A
def unset_key(dotenv_path,key_to_unset,quote_mode=_D):
	B=dotenv_path;A=key_to_unset
	if not os.path.exists(B):logger.warning("Can't delete from %s - it doesn't exist.",B);return _A,A
	C=_B
	with rewrite(B)as(E,F):
		for D in with_warn_for_invalid_lines(parse_stream(E)):
			if D.key==A:C=_C
			else:F.write(D.original.string)
	if not C:logger.warning("Key %s not removed from %s - key doesn't exist.",A,B);return _A,A
	return C,A
def resolve_nested_variables(values):
	def C(name,default):A=default;A=A if A is not _A else'';C=os.getenv(name,B.get(name,A));return C
	def D(match):A=match.groupdict();return C(name=A['name'],default=A['default'])
	B={}
	for(E,A)in values.items():B[E]=__posix_variable.sub(D,A)if A is not _A else _A
	return B
def _walk_to_root(path):
	A=path
	if not os.path.exists(A):raise IOError('Starting path not found')
	if os.path.isfile(A):A=os.path.dirname(A)
	C=_A;B=os.path.abspath(A)
	while C!=B:yield B;D=os.path.abspath(os.path.join(B,os.path.pardir));C,B=B,D
def find_dotenv(filename='.env',raise_error_if_not_found=_B,usecwd=_B):
	E='.py'
	def F():A='__file__';B=__import__('__main__',_A,_A,fromlist=[A]);return not hasattr(B,A)
	if usecwd or F()or getattr(sys,'frozen',_B):B=os.getcwd()
	else:
		A=sys._getframe()
		if PY2 and not __file__.endswith(E):C=__file__.rsplit('.',1)[0]+E
		else:C=__file__
		while A.f_code.co_filename==C:assert A.f_back is not _A;A=A.f_back
		G=A.f_code.co_filename;B=os.path.dirname(os.path.abspath(G))
	for H in _walk_to_root(B):
		D=os.path.join(H,filename)
		if os.path.isfile(D):return D
	if raise_error_if_not_found:raise IOError('File not found')
	return''
def load_dotenv(dotenv_path=_A,stream=_A,verbose=_B,override=_B,interpolate=_C,**A):B=dotenv_path or stream or find_dotenv();return DotEnv(B,verbose=verbose,interpolate=interpolate,**A).set_as_environment_variables(override=override)
def dotenv_values(dotenv_path=_A,stream=_A,verbose=_B,interpolate=_C,**A):B=dotenv_path or stream or find_dotenv();return DotEnv(B,verbose=verbose,interpolate=interpolate,**A).dict()
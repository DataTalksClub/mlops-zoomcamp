from __future__ import print_function
_A='store_true'
from IPython.core.magic import Magics,line_magic,magics_class
from IPython.core.magic_arguments import argument,magic_arguments,parse_argstring
from.main import find_dotenv,load_dotenv
@magics_class
class IPythonDotEnv(Magics):
	@magic_arguments()
	@argument('-o','--override',action=_A,help='Indicate to override existing variables')
	@argument('-v','--verbose',action=_A,help='Indicate function calls to be verbose')
	@argument('dotenv_path',nargs='?',type=str,default='.env',help='Search in increasingly higher folders for the `dotenv_path`')
	@line_magic
	def dotenv(self,line):
		A=parse_argstring(self.dotenv,line);B=A.dotenv_path
		try:B=find_dotenv(B,True,True)
		except IOError:print('cannot find .env file');return
		load_dotenv(B,verbose=A.verbose,override=A.override)
def load_ipython_extension(ipython):ipython.register_magics(IPythonDotEnv)
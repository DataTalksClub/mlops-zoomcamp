_A=None
from.compat import IS_TYPE_CHECKING
from.main import load_dotenv,get_key,set_key,unset_key,find_dotenv,dotenv_values
if IS_TYPE_CHECKING:from typing import Any,Optional
def load_ipython_extension(ipython):from.ipython import load_ipython_extension as A;A(ipython)
def get_cli_string(path=_A,action=_A,key=_A,value=_A,quote=_A):
	D=quote;C=action;B=value;A=['dotenv']
	if D:A.append('-q %s'%D)
	if path:A.append('-f %s'%path)
	if C:
		A.append(C)
		if key:
			A.append(key)
			if B:
				if' 'in B:A.append('"%s"'%B)
				else:A.append(B)
	return' '.join(A).strip()
__all__=['get_cli_string','load_dotenv','dotenv_values','get_key','set_key','unset_key','find_dotenv','load_ipython_extension']
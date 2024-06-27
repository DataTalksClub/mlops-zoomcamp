import sys
PY2=sys.version_info[0]==2
if PY2:from StringIO import StringIO
else:from io import StringIO
def is_type_checking():
	try:from typing import TYPE_CHECKING as A
	except ImportError:return False
	return A
IS_TYPE_CHECKING=is_type_checking()
if IS_TYPE_CHECKING:from typing import Text
def to_env(text):
	if PY2:return text.encode(sys.getfilesystemencoding()or'utf-8')
	else:return text
def to_text(string):
	A=string
	if PY2:return A.decode('utf-8')
	else:return A
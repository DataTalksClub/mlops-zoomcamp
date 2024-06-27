import textwrap
from contextlib import contextmanager
class TextWrapper(textwrap.TextWrapper):
	def _handle_long_word(E,reversed_chunks,cur_line,cur_len,width):
		B=cur_line;A=reversed_chunks;C=max(width-cur_len,1)
		if E.break_long_words:D=A[-1];F=D[:C];G=D[C:];B.append(F);A[-1]=G
		elif not B:B.append(A.pop())
	@contextmanager
	def extra_indent(self,indent):
		B=indent;A=self;C=A.initial_indent;D=A.subsequent_indent;A.initial_indent+=B;A.subsequent_indent+=B
		try:yield
		finally:A.initial_indent=C;A.subsequent_indent=D
	def indent_only(A,text):
		B=[]
		for(D,E)in enumerate(text.splitlines()):
			C=A.initial_indent
			if D>0:C=A.subsequent_indent
			B.append(f"{C}{E}")
		return'\n'.join(B)
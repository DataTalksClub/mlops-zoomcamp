_E=True
_D=False
_C=' '
_B='\n'
_A=None
from contextlib import contextmanager
from._compat import term_len
from.parser import split_opt
from.termui import get_terminal_size
FORCED_WIDTH=_A
def measure_table(rows):
	A={}
	for C in rows:
		for(B,D)in enumerate(C):A[B]=max(A.get(B,0),term_len(D))
	return tuple(A for(B,A)in sorted(A.items()))
def iter_rows(rows,col_count):
	for A in rows:A=tuple(A);yield A+('',)*(col_count-len(A))
def wrap_text(text,width=78,initial_indent='',subsequent_indent='',preserve_paragraphs=_D):
	A=text;from._textwrap import TextWrapper as I;A=A.expandtabs();E=I(width,initial_indent=initial_indent,subsequent_indent=subsequent_indent,replace_whitespace=_D)
	if not preserve_paragraphs:return E.fill(A)
	F=[];C=[];B=_A
	def H():
		if not C:return
		if C[0].strip()=='\x08':F.append((B or 0,_E,_B.join(C[1:])))
		else:F.append((B or 0,_D,_C.join(C)))
		del C[:]
	for D in A.splitlines():
		if not D:H();B=_A
		else:
			if B is _A:J=term_len(D);D=D.lstrip();B=J-term_len(D)
			C.append(D)
	H();G=[]
	for(B,K,A)in F:
		with E.extra_indent(_C*B):
			if K:G.append(E.indent_only(A))
			else:G.append(E.fill(A))
	return'\n\n'.join(G)
class HelpFormatter:
	def __init__(B,indent_increment=2,width=_A,max_width=_A):
		C=max_width;A=width;B.indent_increment=indent_increment
		if C is _A:C=80
		if A is _A:
			A=FORCED_WIDTH
			if A is _A:A=max(min(get_terminal_size()[0],C)-2,50)
		B.width=A;B.current_indent=0;B.buffer=[]
	def write(A,string):A.buffer.append(string)
	def indent(A):A.current_indent+=A.indent_increment
	def dedent(A):A.current_indent-=A.indent_increment
	def write_usage(A,prog,args='',prefix='Usage: '):
		E=prefix;B=f"{E:>{A.current_indent}}{prog} ";D=A.width-A.current_indent
		if D>=term_len(B)+20:C=_C*term_len(B);A.write(wrap_text(args,D,initial_indent=B,subsequent_indent=C))
		else:A.write(B);A.write(_B);C=_C*(max(A.current_indent,term_len(E))+4);A.write(wrap_text(args,D,initial_indent=C,subsequent_indent=C))
		A.write(_B)
	def write_heading(A,heading):A.write(f"{'':>{A.current_indent}}{heading}:\n")
	def write_paragraph(A):
		if A.buffer:A.write(_B)
	def write_text(A,text):C=max(A.width-A.current_indent,11);B=_C*A.current_indent;A.write(wrap_text(text,C,initial_indent=B,subsequent_indent=B,preserve_paragraphs=_E));A.write(_B)
	def write_dl(A,rows,col_max=30,col_spacing=2):
		G=col_spacing;C=rows;C=list(C);E=measure_table(C)
		if len(E)!=2:raise TypeError('Expected two columns for definition list')
		B=min(E[0],col_max)+G
		for(F,H)in iter_rows(C,len(E)):
			A.write(f"{'':>{A.current_indent}}{F}")
			if not H:A.write(_B);continue
			if term_len(F)<=B-G:A.write(_C*(B-term_len(F)))
			else:A.write(_B);A.write(_C*(B+A.current_indent))
			I=max(A.width-B-2,10);J=wrap_text(H,I,preserve_paragraphs=_E);D=J.splitlines()
			if D:
				A.write(f"{D[0]}\n")
				for K in D[1:]:A.write(f"{'':>{B+A.current_indent}}{K}\n")
				if len(D)>1:A.write(_B)
			else:A.write(_B)
	@contextmanager
	def section(self,name):
		A=self;A.write_paragraph();A.write_heading(name);A.indent()
		try:yield
		finally:A.dedent()
	@contextmanager
	def indentation(self):
		self.indent()
		try:yield
		finally:self.dedent()
	def getvalue(A):return''.join(A.buffer)
def join_options(options):
	A=[];B=_D
	for C in options:
		D=split_opt(C)[0]
		if D=='/':B=_E
		A.append((len(D),C))
	A.sort(key=lambda x:x[0]);A=', '.join(A[1]for A in A);return A,B
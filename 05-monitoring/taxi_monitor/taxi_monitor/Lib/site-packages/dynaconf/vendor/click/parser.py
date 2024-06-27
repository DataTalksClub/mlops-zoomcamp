_C='append'
_B='store'
_A=None
import re
from collections import deque
from.exceptions import BadArgumentUsage
from.exceptions import BadOptionUsage
from.exceptions import NoSuchOption
from.exceptions import UsageError
def _unpack_args(args,nargs_spec):
	D=nargs_spec;C=args;C=deque(C);D=deque(D);A=[];B=_A
	def F(c):
		try:
			if B is _A:return c.popleft()
			else:return c.pop()
		except IndexError:return
	while D:
		E=F(D)
		if E==1:A.append(F(C))
		elif E>1:
			G=[F(C)for A in range(E)]
			if B is not _A:G.reverse()
			A.append(tuple(G))
		elif E<0:
			if B is not _A:raise TypeError('Cannot have two nargs < 0')
			B=len(A);A.append(_A)
	if B is not _A:A[B]=tuple(C);C=[];A[B+1:]=reversed(A[B+1:])
	return tuple(A),list(C)
def _error_opt_args(nargs,opt):
	B=nargs;A=opt
	if B==1:raise BadOptionUsage(A,f"{A} option requires an argument")
	raise BadOptionUsage(A,f"{A} option requires {B} arguments")
def split_opt(opt):
	A=opt;B=A[:1]
	if B.isalnum():return'',A
	if A[1:2]==B:return A[:2],A[2:]
	return B,A[1:]
def normalize_opt(opt,ctx):
	B=ctx;A=opt
	if B is _A or B.token_normalize_func is _A:return A
	C,A=split_opt(A);return f"{C}{B.token_normalize_func(A)}"
def split_arg_string(string):
	B=string;C=[]
	for D in re.finditer('(\'([^\'\\\\]*(?:\\\\.[^\'\\\\]*)*)\'|\\"([^\\"\\\\]*(?:\\\\.[^\\"\\\\]*)*)\\"|\\S+)\\s*',B,re.S):
		A=D.group().strip()
		if A[:1]==A[-1:]and A[:1]in'"\'':A=A[1:-1].encode('ascii','backslashreplace').decode('unicode-escape')
		try:A=type(B)(A)
		except UnicodeError:pass
		C.append(A)
	return C
class Option:
	def __init__(A,opts,dest,action=_A,nargs=1,const=_A,obj=_A):
		D=action;A._short_opts=[];A._long_opts=[];A.prefixes=set()
		for B in opts:
			C,E=split_opt(B)
			if not C:raise ValueError(f"Invalid start character for option ({B})")
			A.prefixes.add(C[0])
			if len(C)==1 and len(E)==1:A._short_opts.append(B)
			else:A._long_opts.append(B);A.prefixes.add(C)
		if D is _A:D=_B
		A.dest=dest;A.action=D;A.nargs=nargs;A.const=const;A.obj=obj
	@property
	def takes_value(self):return self.action in(_B,_C)
	def process(A,value,state):
		C=value;B=state
		if A.action==_B:B.opts[A.dest]=C
		elif A.action=='store_const':B.opts[A.dest]=A.const
		elif A.action==_C:B.opts.setdefault(A.dest,[]).append(C)
		elif A.action=='append_const':B.opts.setdefault(A.dest,[]).append(A.const)
		elif A.action=='count':B.opts[A.dest]=B.opts.get(A.dest,0)+1
		else:raise ValueError(f"unknown action '{A.action}'")
		B.order.append(A.obj)
class Argument:
	def __init__(A,dest,nargs=1,obj=_A):A.dest=dest;A.nargs=nargs;A.obj=obj
	def process(A,value,state):
		C=state;B=value
		if A.nargs>1:
			D=sum(1 for A in B if A is _A)
			if D==len(B):B=_A
			elif D!=0:raise BadArgumentUsage(f"argument {A.dest} takes {A.nargs} values")
		C.opts[A.dest]=B;C.order.append(A.obj)
class ParsingState:
	def __init__(A,rargs):A.opts={};A.largs=[];A.rargs=rargs;A.order=[]
class OptionParser:
	def __init__(A,ctx=_A):
		B=ctx;A.ctx=B;A.allow_interspersed_args=True;A.ignore_unknown_options=False
		if B is not _A:A.allow_interspersed_args=B.allow_interspersed_args;A.ignore_unknown_options=B.ignore_unknown_options
		A._short_opt={};A._long_opt={};A._opt_prefixes={'-','--'};A._args=[]
	def add_option(B,opts,dest,action=_A,nargs=1,const=_A,obj=_A):
		D=obj;C=opts
		if D is _A:D=dest
		C=[normalize_opt(A,B.ctx)for A in C];A=Option(C,dest,action=action,nargs=nargs,const=const,obj=D);B._opt_prefixes.update(A.prefixes)
		for E in A._short_opts:B._short_opt[E]=A
		for E in A._long_opts:B._long_opt[E]=A
	def add_argument(B,dest,nargs=1,obj=_A):
		A=obj
		if A is _A:A=dest
		B._args.append(Argument(dest=dest,nargs=nargs,obj=A))
	def parse_args(B,args):
		A=ParsingState(args)
		try:B._process_args_for_options(A);B._process_args_for_args(A)
		except UsageError:
			if B.ctx is _A or not B.ctx.resilient_parsing:raise
		return A.opts,A.largs,A.order
	def _process_args_for_args(B,state):
		A=state;C,D=_unpack_args(A.largs+A.rargs,[A.nargs for A in B._args])
		for(E,F)in enumerate(B._args):F.process(C[E],A)
		A.largs=D;A.rargs=[]
	def _process_args_for_options(C,state):
		B=state
		while B.rargs:
			A=B.rargs.pop(0);D=len(A)
			if A=='--':return
			elif A[:1]in C._opt_prefixes and D>1:C._process_opts(A,B)
			elif C.allow_interspersed_args:B.largs.append(A)
			else:B.rargs.insert(0,A);return
	def _match_long_opt(D,opt,explicit_value,state):
		E=explicit_value;B=state;A=opt
		if A not in D._long_opt:H=[B for B in D._long_opt if B.startswith(A)];raise NoSuchOption(A,possibilities=H,ctx=D.ctx)
		F=D._long_opt[A]
		if F.takes_value:
			if E is not _A:B.rargs.insert(0,E)
			C=F.nargs
			if len(B.rargs)<C:_error_opt_args(C,A)
			elif C==1:G=B.rargs.pop(0)
			else:G=tuple(B.rargs[:C]);del B.rargs[:C]
		elif E is not _A:raise BadOptionUsage(A,f"{A} option does not take a value")
		else:G=_A
		F.process(G,B)
	def _match_short_opt(B,arg,state):
		D=arg;A=state;J=False;F=1;K=D[0];G=[]
		for L in D[1:]:
			H=normalize_opt(f"{K}{L}",B.ctx);E=B._short_opt.get(H);F+=1
			if not E:
				if B.ignore_unknown_options:G.append(L);continue
				raise NoSuchOption(H,ctx=B.ctx)
			if E.takes_value:
				if F<len(D):A.rargs.insert(0,D[F:]);J=True
				C=E.nargs
				if len(A.rargs)<C:_error_opt_args(C,H)
				elif C==1:I=A.rargs.pop(0)
				else:I=tuple(A.rargs[:C]);del A.rargs[:C]
			else:I=_A
			E.process(I,A)
			if J:break
		if B.ignore_unknown_options and G:A.largs.append(f"{K}{''.join(G)}")
	def _process_opts(B,arg,state):
		C=state;A=arg;D=_A
		if'='in A:E,D=A.split('=',1)
		else:E=A
		F=normalize_opt(E,B.ctx)
		try:B._match_long_opt(F,D,C)
		except NoSuchOption:
			if A[:2]not in B._opt_prefixes:return B._match_short_opt(A,C)
			if not B.ignore_unknown_options:raise
			C.largs.append(A)
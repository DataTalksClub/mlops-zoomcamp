_E='default'
_D='nargs'
_C=True
_B=False
_A=None
import errno,inspect,os,sys
from contextlib import contextmanager
from functools import update_wrapper
from itertools import repeat
from._unicodefun import _verify_python_env
from.exceptions import Abort
from.exceptions import BadParameter
from.exceptions import ClickException
from.exceptions import Exit
from.exceptions import MissingParameter
from.exceptions import UsageError
from.formatting import HelpFormatter
from.formatting import join_options
from.globals import pop_context
from.globals import push_context
from.parser import OptionParser
from.parser import split_opt
from.termui import confirm
from.termui import prompt
from.termui import style
from.types import BOOL
from.types import convert_type
from.types import IntRange
from.utils import echo
from.utils import make_default_short_help
from.utils import make_str
from.utils import PacifyFlushWrapper
_missing=object()
SUBCOMMAND_METAVAR='COMMAND [ARGS]...'
SUBCOMMANDS_METAVAR='COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...'
DEPRECATED_HELP_NOTICE=' (DEPRECATED)'
DEPRECATED_INVOKE_NOTICE='DeprecationWarning: The command {name} is deprecated.'
def _maybe_show_deprecated_notice(cmd):
	if cmd.deprecated:echo(style(DEPRECATED_INVOKE_NOTICE.format(name=cmd.name),fg='red'),err=_C)
def fast_exit(code):sys.stdout.flush();sys.stderr.flush();os._exit(code)
def _bashcomplete(cmd,prog_name,complete_var=_A):
	B=prog_name;A=complete_var
	if A is _A:A=f"_{B}_COMPLETE".replace('-','_').upper()
	C=os.environ.get(A)
	if not C:return
	from._bashcomplete import bashcomplete as D
	if D(cmd,B,A,C):fast_exit(1)
def _check_multicommand(base_command,cmd_name,cmd,register=_B):
	B=cmd_name;A=base_command
	if not A.chain or not isinstance(cmd,MultiCommand):return
	if register:C='It is not possible to add multi commands as children to another multi command that is in chain mode.'
	else:C='Found a multi command as subcommand to a multi command that is in chain mode. This is not supported.'
	raise RuntimeError(f"{C}. Command {A.name!r} is set to chain and {B!r} was added as a subcommand but it in itself is a multi command. ({B!r} is a {type(cmd).__name__} within a chained {type(A).__name__} named {A.name!r}).")
def batch(iterable,batch_size):return list(zip(*repeat(iter(iterable),batch_size)))
@contextmanager
def augment_usage_errors(ctx,param=_A):
	B=param
	try:yield
	except BadParameter as A:
		if A.ctx is _A:A.ctx=ctx
		if B is not _A and A.param is _A:A.param=B
		raise
	except UsageError as A:
		if A.ctx is _A:A.ctx=ctx
		raise
def iter_params_for_processing(invocation_order,declaration_order):
	def A(item):
		try:A=invocation_order.index(item)
		except ValueError:A=float('inf')
		return not item.is_eager,A
	return sorted(declaration_order,key=A)
class ParameterSource:
	COMMANDLINE='COMMANDLINE';ENVIRONMENT='ENVIRONMENT';DEFAULT='DEFAULT';DEFAULT_MAP='DEFAULT_MAP';VALUES={COMMANDLINE,ENVIRONMENT,DEFAULT,DEFAULT_MAP}
	@classmethod
	def validate(A,value):
		B=value
		if B not in A.VALUES:raise ValueError(f"Invalid ParameterSource value: {B!r}. Valid values are: {','.join(A.VALUES)}")
class Context:
	def __init__(A,command,parent=_A,info_name=_A,obj=_A,auto_envvar_prefix=_A,default_map=_A,terminal_width=_A,max_content_width=_A,resilient_parsing=_B,allow_extra_args=_A,allow_interspersed_args=_A,ignore_unknown_options=_A,help_option_names=_A,token_normalize_func=_A,color=_A,show_default=_A):
		O=info_name;N=color;M=token_normalize_func;L=ignore_unknown_options;K=allow_interspersed_args;J=allow_extra_args;I=max_content_width;H=terminal_width;G=default_map;F=obj;E=help_option_names;D=command;C=auto_envvar_prefix;B=parent;A.parent=B;A.command=D;A.info_name=O;A.params={};A.args=[];A.protected_args=[]
		if F is _A and B is not _A:F=B.obj
		A.obj=F;A._meta=getattr(B,'meta',{})
		if G is _A and B is not _A and B.default_map is not _A:G=B.default_map.get(O)
		A.default_map=G;A.invoked_subcommand=_A
		if H is _A and B is not _A:H=B.terminal_width
		A.terminal_width=H
		if I is _A and B is not _A:I=B.max_content_width
		A.max_content_width=I
		if J is _A:J=D.allow_extra_args
		A.allow_extra_args=J
		if K is _A:K=D.allow_interspersed_args
		A.allow_interspersed_args=K
		if L is _A:L=D.ignore_unknown_options
		A.ignore_unknown_options=L
		if E is _A:
			if B is not _A:E=B.help_option_names
			else:E=['--help']
		A.help_option_names=E
		if M is _A and B is not _A:M=B.token_normalize_func
		A.token_normalize_func=M;A.resilient_parsing=resilient_parsing
		if C is _A:
			if B is not _A and B.auto_envvar_prefix is not _A and A.info_name is not _A:C=f"{B.auto_envvar_prefix}_{A.info_name.upper()}"
		else:C=C.upper()
		if C is not _A:C=C.replace('-','_')
		A.auto_envvar_prefix=C
		if N is _A and B is not _A:N=B.color
		A.color=N;A.show_default=show_default;A._close_callbacks=[];A._depth=0;A._source_by_paramname={}
	def __enter__(A):A._depth+=1;push_context(A);return A
	def __exit__(A,exc_type,exc_value,tb):
		A._depth-=1
		if A._depth==0:A.close()
		pop_context()
	@contextmanager
	def scope(self,cleanup=_C):
		B=cleanup;A=self
		if not B:A._depth+=1
		try:
			with A as C:yield C
		finally:
			if not B:A._depth-=1
	@property
	def meta(self):return self._meta
	def make_formatter(A):return HelpFormatter(width=A.terminal_width,max_width=A.max_content_width)
	def call_on_close(A,f):A._close_callbacks.append(f);return f
	def close(A):
		for B in A._close_callbacks:B()
		A._close_callbacks=[]
	@property
	def command_path(self):
		A=self;B=''
		if A.info_name is not _A:B=A.info_name
		if A.parent is not _A:B=f"{A.parent.command_path} {B}"
		return B.lstrip()
	def find_root(B):
		A=B
		while A.parent is not _A:A=A.parent
		return A
	def find_object(B,object_type):
		A=B
		while A is not _A:
			if isinstance(A.obj,object_type):return A.obj
			A=A.parent
	def ensure_object(B,object_type):
		C=object_type;A=B.find_object(C)
		if A is _A:B.obj=A=C()
		return A
	def lookup_default(B,name):
		if B.default_map is not _A:
			A=B.default_map.get(name)
			if callable(A):A=A()
			return A
	def fail(A,message):raise UsageError(message,A)
	def abort(A):raise Abort()
	def exit(A,code=0):raise Exit(code)
	def get_usage(A):return A.command.get_usage(A)
	def get_help(A):return A.command.get_help(A)
	def invoke(*B,**E):
		F,A=B[:2];G=F
		if isinstance(A,Command):
			C=A;A=C.callback;G=Context(C,info_name=C.name,parent=F)
			if A is _A:raise TypeError('The given command does not have a callback that can be invoked.')
			for D in C.params:
				if D.name not in E and D.expose_value:E[D.name]=D.get_default(G)
		B=B[2:]
		with augment_usage_errors(F):
			with G:return A(*B,**E)
	def forward(*E,**A):
		B,D=E[:2]
		if not isinstance(D,Command):raise TypeError('Callback is not a command.')
		for C in B.params:
			if C not in A:A[C]=B.params[C]
		return B.invoke(D,**A)
	def set_parameter_source(B,name,source):A=source;ParameterSource.validate(A);B._source_by_paramname[name]=A
	def get_parameter_source(A,name):return A._source_by_paramname[name]
class BaseCommand:
	allow_extra_args=_B;allow_interspersed_args=_C;ignore_unknown_options=_B
	def __init__(B,name,context_settings=_A):
		A=context_settings;B.name=name
		if A is _A:A={}
		B.context_settings=A
	def __repr__(A):return f"<{A.__class__.__name__} {A.name}>"
	def get_usage(A,ctx):raise NotImplementedError('Base commands cannot get usage')
	def get_help(A,ctx):raise NotImplementedError('Base commands cannot get help')
	def make_context(A,info_name,args,parent=_A,**B):
		for(D,E)in A.context_settings.items():
			if D not in B:B[D]=E
		C=Context(A,info_name=info_name,parent=parent,**B)
		with C.scope(cleanup=_B):A.parse_args(C,args)
		return C
	def parse_args(A,ctx,args):raise NotImplementedError('Base commands do not know how to parse arguments.')
	def invoke(A,ctx):raise NotImplementedError('Base commands are not invokable by default')
	def main(E,args=_A,prog_name=_A,complete_var=_A,standalone_mode=_C,**G):
		D=standalone_mode;C=prog_name;B=args;_verify_python_env()
		if B is _A:B=sys.argv[1:]
		else:B=list(B)
		if C is _A:C=make_str(os.path.basename(sys.argv[0]if sys.argv else __file__))
		_bashcomplete(E,C,complete_var)
		try:
			try:
				with E.make_context(C,B,**G)as F:
					H=E.invoke(F)
					if not D:return H
					F.exit()
			except(EOFError,KeyboardInterrupt):echo(file=sys.stderr);raise Abort()
			except ClickException as A:
				if not D:raise
				A.show();sys.exit(A.exit_code)
			except OSError as A:
				if A.errno==errno.EPIPE:sys.stdout=PacifyFlushWrapper(sys.stdout);sys.stderr=PacifyFlushWrapper(sys.stderr);sys.exit(1)
				else:raise
		except Exit as A:
			if D:sys.exit(A.exit_code)
			else:return A.exit_code
		except Abort:
			if not D:raise
			echo('Aborted!',file=sys.stderr);sys.exit(1)
	def __call__(A,*B,**C):return A.main(*B,**C)
class Command(BaseCommand):
	def __init__(A,name,context_settings=_A,callback=_A,params=_A,help=_A,epilog=_A,short_help=_A,options_metavar='[OPTIONS]',add_help_option=_C,no_args_is_help=_B,hidden=_B,deprecated=_B):
		B='\x0c';BaseCommand.__init__(A,name,context_settings);A.callback=callback;A.params=params or[]
		if help and B in help:help=help.split(B,1)[0]
		A.help=help;A.epilog=epilog;A.options_metavar=options_metavar;A.short_help=short_help;A.add_help_option=add_help_option;A.no_args_is_help=no_args_is_help;A.hidden=hidden;A.deprecated=deprecated
	def __repr__(A):return f"<{A.__class__.__name__} {A.name}>"
	def get_usage(B,ctx):A=ctx.make_formatter();B.format_usage(ctx,A);return A.getvalue().rstrip('\n')
	def get_params(B,ctx):
		A=B.params;C=B.get_help_option(ctx)
		if C is not _A:A=A+[C]
		return A
	def format_usage(A,ctx,formatter):B=A.collect_usage_pieces(ctx);formatter.write_usage(ctx.command_path,' '.join(B))
	def collect_usage_pieces(A,ctx):
		B=[A.options_metavar]
		for C in A.get_params(ctx):B.extend(C.get_usage_pieces(ctx))
		return B
	def get_help_option_names(C,ctx):
		A=set(ctx.help_option_names)
		for B in C.params:A.difference_update(B.opts);A.difference_update(B.secondary_opts)
		return A
	def get_help_option(A,ctx):
		B=A.get_help_option_names(ctx)
		if not B or not A.add_help_option:return
		def C(ctx,param,value):
			A=ctx
			if value and not A.resilient_parsing:echo(A.get_help(),color=A.color);A.exit()
		return Option(B,is_flag=_C,is_eager=_C,expose_value=_B,callback=C,help='Show this message and exit.')
	def make_parser(C,ctx):
		A=ctx;B=OptionParser(A)
		for D in C.get_params(A):D.add_to_parser(B,A)
		return B
	def get_help(B,ctx):A=ctx.make_formatter();B.format_help(ctx,A);return A.getvalue().rstrip('\n')
	def get_short_help_str(A,limit=45):return A.short_help or A.help and make_default_short_help(A.help,limit)or''
	def format_help(A,ctx,formatter):C=formatter;B=ctx;A.format_usage(B,C);A.format_help_text(B,C);A.format_options(B,C);A.format_epilog(B,C)
	def format_help_text(B,ctx,formatter):
		A=formatter
		if B.help:
			A.write_paragraph()
			with A.indentation():
				C=B.help
				if B.deprecated:C+=DEPRECATED_HELP_NOTICE
				A.write_text(C)
		elif B.deprecated:
			A.write_paragraph()
			with A.indentation():A.write_text(DEPRECATED_HELP_NOTICE)
	def format_options(D,ctx,formatter):
		B=formatter;A=[]
		for E in D.get_params(ctx):
			C=E.get_help_record(ctx)
			if C is not _A:A.append(C)
		if A:
			with B.section('Options'):B.write_dl(A)
	def format_epilog(B,ctx,formatter):
		A=formatter
		if B.epilog:
			A.write_paragraph()
			with A.indentation():A.write_text(B.epilog)
	def parse_args(C,ctx,args):
		B=args;A=ctx
		if not B and C.no_args_is_help and not A.resilient_parsing:echo(A.get_help(),color=A.color);A.exit()
		D=C.make_parser(A);E,B,F=D.parse_args(args=B)
		for G in iter_params_for_processing(F,C.get_params(A)):H,B=G.handle_parse_result(A,E,B)
		if B and not A.allow_extra_args and not A.resilient_parsing:A.fail(f"Got unexpected extra argument{'s'if len(B)!=1 else''} ({' '.join(map(make_str,B))})")
		A.args=B;return B
	def invoke(A,ctx):
		_maybe_show_deprecated_notice(A)
		if A.callback is not _A:return ctx.invoke(A.callback,**ctx.params)
class MultiCommand(Command):
	allow_extra_args=_C;allow_interspersed_args=_B
	def __init__(A,name=_A,invoke_without_command=_B,no_args_is_help=_A,subcommand_metavar=_A,chain=_B,result_callback=_A,**G):
		E=chain;D=invoke_without_command;C=no_args_is_help;B=subcommand_metavar;Command.__init__(A,name,**G)
		if C is _A:C=not D
		A.no_args_is_help=C;A.invoke_without_command=D
		if B is _A:
			if E:B=SUBCOMMANDS_METAVAR
			else:B=SUBCOMMAND_METAVAR
		A.subcommand_metavar=B;A.chain=E;A.result_callback=result_callback
		if A.chain:
			for F in A.params:
				if isinstance(F,Argument)and not F.required:raise RuntimeError('Multi commands in chain mode cannot have optional arguments.')
	def collect_usage_pieces(A,ctx):B=Command.collect_usage_pieces(A,ctx);B.append(A.subcommand_metavar);return B
	def format_options(A,ctx,formatter):B=formatter;Command.format_options(A,ctx,B);A.format_commands(ctx,B)
	def resultcallback(A,replace=_B):
		def B(f):
			B=A.result_callback
			if B is _A or replace:A.result_callback=f;return f
			def C(__value,*A,**C):return f(B(__value,*A,**C),*A,**C)
			A.result_callback=D=update_wrapper(C,f);return D
		return B
	def format_commands(F,ctx,formatter):
		D=formatter;B=[]
		for C in F.list_commands(ctx):
			A=F.get_command(ctx,C)
			if A is _A:continue
			if A.hidden:continue
			B.append((C,A))
		if len(B):
			G=D.width-6-max(len(A[0])for A in B);E=[]
			for(C,A)in B:help=A.get_short_help_str(G);E.append((C,help))
			if E:
				with D.section('Commands'):D.write_dl(E)
	def parse_args(C,ctx,args):
		A=ctx
		if not args and C.no_args_is_help and not A.resilient_parsing:echo(A.get_help(),color=A.color);A.exit()
		B=Command.parse_args(C,A,args)
		if C.chain:A.protected_args=B;A.args=[]
		elif B:A.protected_args,A.args=B[:1],B[1:]
		return A.args
	def invoke(B,ctx):
		A=ctx
		def F(value):
			C=value
			if B.result_callback is not _A:C=A.invoke(B.result_callback,C,**A.params)
			return C
		if not A.protected_args:
			if B.invoke_without_command:
				if not B.chain:return Command.invoke(B,A)
				with A:Command.invoke(B,A);return F([])
			A.fail('Missing command.')
		D=A.protected_args+A.args;A.args=[];A.protected_args=[]
		if not B.chain:
			with A:
				E,G,D=B.resolve_command(A,D);A.invoked_subcommand=E;Command.invoke(B,A);C=G.make_context(E,D,parent=A)
				with C:return F(C.command.invoke(C))
		with A:
			A.invoked_subcommand='*'if D else _A;Command.invoke(B,A);H=[]
			while D:E,G,D=B.resolve_command(A,D);C=G.make_context(E,D,parent=A,allow_extra_args=_C,allow_interspersed_args=_B);H.append(C);D,C.args=C.args,[]
			I=[]
			for C in H:
				with C:I.append(C.command.invoke(C))
			return F(I)
	def resolve_command(D,ctx,args):
		A=ctx;B=make_str(args[0]);E=B;C=D.get_command(A,B)
		if C is _A and A.token_normalize_func is not _A:B=A.token_normalize_func(B);C=D.get_command(A,B)
		if C is _A and not A.resilient_parsing:
			if split_opt(B)[0]:D.parse_args(A,A.args)
			A.fail(f"No such command '{E}'.")
		return B,C,args[1:]
	def get_command(A,ctx,cmd_name):raise NotImplementedError()
	def list_commands(A,ctx):return[]
class Group(MultiCommand):
	def __init__(A,name=_A,commands=_A,**B):MultiCommand.__init__(A,name,**B);A.commands=commands or{}
	def add_command(C,cmd,name=_A):
		B=cmd;A=name;A=A or B.name
		if A is _A:raise TypeError('Command has no name.')
		_check_multicommand(C,A,B,register=_C);C.commands[A]=B
	def command(B,*C,**D):
		from.decorators import command as E
		def A(f):A=E(*C,**D)(f);B.add_command(A);return A
		return A
	def group(B,*C,**D):
		from.decorators import group
		def A(f):A=group(*C,**D)(f);B.add_command(A);return A
		return A
	def get_command(A,ctx,cmd_name):return A.commands.get(cmd_name)
	def list_commands(A,ctx):return sorted(A.commands)
class CommandCollection(MultiCommand):
	def __init__(A,name=_A,sources=_A,**B):MultiCommand.__init__(A,name,**B);A.sources=sources or[]
	def add_source(A,multi_cmd):A.sources.append(multi_cmd)
	def get_command(A,ctx,cmd_name):
		C=cmd_name
		for D in A.sources:
			B=D.get_command(ctx,C)
			if B is not _A:
				if A.chain:_check_multicommand(A,C,B)
				return B
	def list_commands(B,ctx):
		A=set()
		for C in B.sources:A.update(C.list_commands(ctx))
		return sorted(A)
class Parameter:
	param_type_name='parameter'
	def __init__(A,param_decls=_A,type=_A,required=_B,default=_A,callback=_A,nargs=_A,metavar=_A,expose_value=_C,is_eager=_B,envvar=_A,autocompletion=_A):
		D=expose_value;C=default;B=nargs;A.name,A.opts,A.secondary_opts=A._parse_decls(param_decls or(),D);A.type=convert_type(type,C)
		if B is _A:
			if A.type.is_composite:B=A.type.arity
			else:B=1
		A.required=required;A.callback=callback;A.nargs=B;A.multiple=_B;A.expose_value=D;A.default=C;A.is_eager=is_eager;A.metavar=metavar;A.envvar=envvar;A.autocompletion=autocompletion
	def __repr__(A):return f"<{A.__class__.__name__} {A.name}>"
	@property
	def human_readable_name(self):return self.name
	def make_metavar(A):
		if A.metavar is not _A:return A.metavar
		B=A.type.get_metavar(A)
		if B is _A:B=A.type.name.upper()
		if A.nargs!=1:B+='...'
		return B
	def get_default(A,ctx):
		if callable(A.default):B=A.default()
		else:B=A.default
		return A.type_cast_value(ctx,B)
	def add_to_parser(A,parser,ctx):0
	def consume_value(B,ctx,opts):
		C=ctx;A=opts.get(B.name);D=ParameterSource.COMMANDLINE
		if A is _A:A=B.value_from_envvar(C);D=ParameterSource.ENVIRONMENT
		if A is _A:A=C.lookup_default(B.name);D=ParameterSource.DEFAULT_MAP
		if A is not _A:C.set_parameter_source(B.name,D)
		return A
	def type_cast_value(A,ctx,value):
		C=value;B=ctx
		if A.type.is_composite:
			if A.nargs<=1:raise TypeError(f"Attempted to invoke composite type but nargs has been set to {A.nargs}. This is not supported; nargs needs to be set to a fixed value > 1.")
			if A.multiple:return tuple(A.type(C or(),A,B)for C in C or())
			return A.type(C or(),A,B)
		def D(value,level):
			E=level;C=value
			if E==0:return A.type(C,A,B)
			return tuple(D(A,E-1)for A in C or())
		return D(C,(A.nargs!=1)+bool(A.multiple))
	def process_value(B,ctx,value):
		A=value
		if A is not _A:return B.type_cast_value(ctx,A)
	def value_is_missing(A,value):
		B=value
		if B is _A:return _C
		if(A.nargs!=1 or A.multiple)and B==():return _C
		return _B
	def full_process_value(B,ctx,value):
		C=ctx;A=value;A=B.process_value(C,A)
		if A is _A and not C.resilient_parsing:
			A=B.get_default(C)
			if A is not _A:C.set_parameter_source(B.name,ParameterSource.DEFAULT)
		if B.required and B.value_is_missing(A):raise MissingParameter(ctx=C,param=B)
		return A
	def resolve_envvar_value(B,ctx):
		if B.envvar is _A:return
		if isinstance(B.envvar,(tuple,list)):
			for C in B.envvar:
				A=os.environ.get(C)
				if A is not _A:return A
		else:
			A=os.environ.get(B.envvar)
			if A!='':return A
	def value_from_envvar(B,ctx):
		A=B.resolve_envvar_value(ctx)
		if A is not _A and B.nargs!=1:A=B.type.split_envvar_value(A)
		return A
	def handle_parse_result(A,ctx,opts,args):
		B=ctx
		with augment_usage_errors(B,param=A):
			C=A.consume_value(B,opts)
			try:C=A.full_process_value(B,C)
			except Exception:
				if not B.resilient_parsing:raise
				C=_A
			if A.callback is not _A:
				try:C=A.callback(B,A,C)
				except Exception:
					if not B.resilient_parsing:raise
		if A.expose_value:B.params[A.name]=C
		return C,args
	def get_help_record(A,ctx):0
	def get_usage_pieces(A,ctx):return[]
	def get_error_hint(A,ctx):B=A.opts or[A.human_readable_name];return' / '.join(repr(A)for A in B)
class Option(Parameter):
	param_type_name='option'
	def __init__(A,param_decls=_A,show_default=_B,prompt=_B,confirmation_prompt=_B,hide_input=_B,is_flag=_A,flag_value=_A,multiple=_B,count=_B,allow_from_autoenv=_C,type=_A,help=_A,hidden=_B,show_choices=_C,show_envvar=_B,**G):
		F=count;D=prompt;C=flag_value;B=is_flag;H=G.get(_E,_missing)is _missing;Parameter.__init__(A,param_decls,type=type,**G)
		if D is _C:E=A.name.replace('_',' ').capitalize()
		elif D is _B:E=_A
		else:E=D
		A.prompt=E;A.confirmation_prompt=confirmation_prompt;A.hide_input=hide_input;A.hidden=hidden
		if B is _A:
			if C is not _A:B=_C
			else:B=bool(A.secondary_opts)
		if B and H:A.default=_B
		if C is _A:C=not A.default
		A.is_flag=B;A.flag_value=C
		if A.is_flag and isinstance(A.flag_value,bool)and type in[_A,bool]:A.type=BOOL;A.is_bool_flag=_C
		else:A.is_bool_flag=_B
		A.count=F
		if F:
			if type is _A:A.type=IntRange(min=0)
			if H:A.default=0
		A.multiple=multiple;A.allow_from_autoenv=allow_from_autoenv;A.help=help;A.show_default=show_default;A.show_choices=show_choices;A.show_envvar=show_envvar
		if __debug__:
			if A.nargs<0:raise TypeError('Options cannot have nargs < 0')
			if A.prompt and A.is_flag and not A.is_bool_flag:raise TypeError('Cannot prompt for flags that are not bools.')
			if not A.is_bool_flag and A.secondary_opts:raise TypeError('Got secondary option for non boolean flag.')
			if A.is_bool_flag and A.hide_input and A.prompt is not _A:raise TypeError('Hidden input does not work with boolean flag prompts.')
			if A.count:
				if A.multiple:raise TypeError('Options cannot be multiple and count at the same time.')
				elif A.is_flag:raise TypeError('Options cannot be count and flags at the same time.')
	def _parse_decls(I,decls,expose_value):
		C=[];F=[];A=_A;D=[]
		for B in decls:
			if B.isidentifier():
				if A is not _A:raise TypeError('Name defined twice')
				A=B
			else:
				H=';'if B[:1]=='/'else'/'
				if H in B:
					E,G=B.split(H,1);E=E.rstrip()
					if E:D.append(split_opt(E));C.append(E)
					G=G.lstrip()
					if G:F.append(G.lstrip())
				else:D.append(split_opt(B));C.append(B)
		if A is _A and D:
			D.sort(key=lambda x:-len(x[0]));A=D[0][1].replace('-','_').lower()
			if not A.isidentifier():A=_A
		if A is _A:
			if not expose_value:return _A,C,F
			raise TypeError('Could not determine name for option')
		if not C and not F:raise TypeError(f"No options defined but a name was passed ({A}). Did you mean to declare an argument instead of an option?")
		return A,C,F
	def add_to_parser(A,parser,ctx):
		C=parser;B={'dest':A.name,_D:A.nargs,'obj':A}
		if A.multiple:D='append'
		elif A.count:D='count'
		else:D='store'
		if A.is_flag:
			B.pop(_D,_A);E=f"{D}_const"
			if A.is_bool_flag and A.secondary_opts:C.add_option(A.opts,action=E,const=_C,**B);C.add_option(A.secondary_opts,action=E,const=_B,**B)
			else:C.add_option(A.opts,action=E,const=A.flag_value,**B)
		else:B['action']=D;C.add_option(A.opts,**B)
	def get_help_record(A,ctx):
		E=ctx
		if A.hidden:return
		F=[]
		def G(opts):
			B,C=join_options(opts)
			if C:F[:]=[_C]
			if not A.is_flag and not A.count:B+=f" {A.make_metavar()}"
			return B
		H=[G(A.opts)]
		if A.secondary_opts:H.append(G(A.secondary_opts))
		help=A.help or'';C=[]
		if A.show_envvar:
			B=A.envvar
			if B is _A:
				if A.allow_from_autoenv and E.auto_envvar_prefix is not _A:B=f"{E.auto_envvar_prefix}_{A.name.upper()}"
			if B is not _A:J=', '.join(str(A)for A in B)if isinstance(B,(list,tuple))else B;C.append(f"env var: {J}")
		if A.default is not _A and(A.show_default or E.show_default):
			if isinstance(A.show_default,str):D=f"({A.show_default})"
			elif isinstance(A.default,(list,tuple)):D=', '.join(str(A)for A in A.default)
			elif inspect.isfunction(A.default):D='(dynamic)'
			else:D=A.default
			C.append(f"default: {D}")
		if A.required:C.append('required')
		if C:I=';'.join(C);help=f"{help}  [{I}]"if help else f"[{I}]"
		return('; 'if F else' / ').join(H),help
	def get_default(A,ctx):
		if A.is_flag and not A.is_bool_flag:
			for B in ctx.command.params:
				if B.name==A.name and B.default:return B.flag_value
			return
		return Parameter.get_default(A,ctx)
	def prompt_for_value(A,ctx):
		B=A.get_default(ctx)
		if A.is_bool_flag:return confirm(A.prompt,B)
		return prompt(A.prompt,default=B,type=A.type,hide_input=A.hide_input,show_choices=A.show_choices,confirmation_prompt=A.confirmation_prompt,value_proc=lambda x:A.process_value(ctx,x))
	def resolve_envvar_value(A,ctx):
		B=ctx;C=Parameter.resolve_envvar_value(A,B)
		if C is not _A:return C
		if A.allow_from_autoenv and B.auto_envvar_prefix is not _A:D=f"{B.auto_envvar_prefix}_{A.name.upper()}";return os.environ.get(D)
	def value_from_envvar(A,ctx):
		B=A.resolve_envvar_value(ctx)
		if B is _A:return
		C=(A.nargs!=1)+bool(A.multiple)
		if C>0 and B is not _A:
			B=A.type.split_envvar_value(B)
			if A.multiple and A.nargs!=1:B=batch(B,A.nargs)
		return B
	def full_process_value(A,ctx,value):
		C=value;B=ctx
		if C is _A and A.prompt is not _A and not B.resilient_parsing:return A.prompt_for_value(B)
		return Parameter.full_process_value(A,B,C)
class Argument(Parameter):
	param_type_name='argument'
	def __init__(B,param_decls,required=_A,**C):
		A=required
		if A is _A:
			if C.get(_E)is not _A:A=_B
			else:A=C.get(_D,1)>0
		Parameter.__init__(B,param_decls,required=A,**C)
		if B.default is not _A and B.nargs<0:raise TypeError('nargs=-1 in combination with a default value is not supported.')
	@property
	def human_readable_name(self):
		A=self
		if A.metavar is not _A:return A.metavar
		return A.name.upper()
	def make_metavar(A):
		if A.metavar is not _A:return A.metavar
		B=A.type.get_metavar(A)
		if not B:B=A.name.upper()
		if not A.required:B=f"[{B}]"
		if A.nargs!=1:B+='...'
		return B
	def _parse_decls(D,decls,expose_value):
		A=decls
		if not A:
			if not expose_value:return _A,[],[]
			raise TypeError('Could not determine name for argument')
		if len(A)==1:B=C=A[0];B=B.replace('-','_').lower()
		else:raise TypeError(f"Arguments take exactly one parameter declaration, got {len(A)}.")
		return B,[C],[]
	def get_usage_pieces(A,ctx):return[A.make_metavar()]
	def get_error_hint(A,ctx):return repr(A.make_metavar())
	def add_to_parser(A,parser,ctx):parser.add_argument(dest=A.name,nargs=A.nargs,obj=A)
_A=None
from._compat import filename_to_ui,get_text_stderr
from.utils import echo
def _join_param_hints(param_hint):
	A=param_hint
	if isinstance(A,(tuple,list)):return' / '.join(repr(A)for A in A)
	return A
class ClickException(Exception):
	exit_code=1
	def __init__(B,message):A=message;super().__init__(A);B.message=A
	def format_message(A):return A.message
	def __str__(A):return A.message
	def show(B,file=_A):
		A=file
		if A is _A:A=get_text_stderr()
		echo(f"Error: {B.format_message()}",file=A)
class UsageError(ClickException):
	exit_code=2
	def __init__(A,message,ctx=_A):ClickException.__init__(A,message);A.ctx=ctx;A.cmd=A.ctx.command if A.ctx else _A
	def show(A,file=_A):
		B=file
		if B is _A:B=get_text_stderr()
		C=_A;D=''
		if A.cmd is not _A and A.cmd.get_help_option(A.ctx)is not _A:D=f"Try '{A.ctx.command_path} {A.ctx.help_option_names[0]}' for help.\n"
		if A.ctx is not _A:C=A.ctx.color;echo(f"{A.ctx.get_usage()}\n{D}",file=B,color=C)
		echo(f"Error: {A.format_message()}",file=B,color=C)
class BadParameter(UsageError):
	def __init__(A,message,ctx=_A,param=_A,param_hint=_A):UsageError.__init__(A,message,ctx);A.param=param;A.param_hint=param_hint
	def format_message(A):
		if A.param_hint is not _A:B=A.param_hint
		elif A.param is not _A:B=A.param.get_error_hint(A.ctx)
		else:return f"Invalid value: {A.message}"
		B=_join_param_hints(B);return f"Invalid value for {B}: {A.message}"
class MissingParameter(BadParameter):
	def __init__(A,message=_A,ctx=_A,param=_A,param_hint=_A,param_type=_A):BadParameter.__init__(A,message,ctx,param,param_hint);A.param_type=param_type
	def format_message(A):
		if A.param_hint is not _A:B=A.param_hint
		elif A.param is not _A:B=A.param.get_error_hint(A.ctx)
		else:B=_A
		B=_join_param_hints(B);D=A.param_type
		if D is _A and A.param is not _A:D=A.param.param_type_name
		C=A.message
		if A.param is not _A:
			E=A.param.type.get_missing_message(A.param)
			if E:
				if C:C+=f".  {E}"
				else:C=E
		F=f" {B}"if B else'';return f"Missing {D}{F}.{' 'if C else''}{C or''}"
	def __str__(A):
		if A.message is _A:B=A.param.name if A.param else _A;return f"missing parameter: {B}"
		else:return A.message
class NoSuchOption(UsageError):
	def __init__(A,option_name,message=_A,possibilities=_A,ctx=_A):
		C=option_name;B=message
		if B is _A:B=f"no such option: {C}"
		UsageError.__init__(A,B,ctx);A.option_name=C;A.possibilities=possibilities
	def format_message(A):
		B=[A.message]
		if A.possibilities:
			if len(A.possibilities)==1:B.append(f"Did you mean {A.possibilities[0]}?")
			else:C=sorted(A.possibilities);B.append(f"(Possible options: {', '.join(C)})")
		return'  '.join(B)
class BadOptionUsage(UsageError):
	def __init__(A,option_name,message,ctx=_A):UsageError.__init__(A,message,ctx);A.option_name=option_name
class BadArgumentUsage(UsageError):
	def __init__(A,message,ctx=_A):UsageError.__init__(A,message,ctx)
class FileError(ClickException):
	def __init__(A,filename,hint=_A):
		C=filename;B=hint;D=filename_to_ui(C)
		if B is _A:B='unknown error'
		ClickException.__init__(A,B);A.ui_filename=D;A.filename=C
	def format_message(A):return f"Could not open file {A.ui_filename}: {A.message}"
class Abort(RuntimeError):0
class Exit(RuntimeError):
	__slots__='exit_code',
	def __init__(A,code=0):A.exit_code=code
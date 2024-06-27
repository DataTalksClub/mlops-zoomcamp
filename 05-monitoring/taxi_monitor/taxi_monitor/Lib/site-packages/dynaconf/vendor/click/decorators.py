_J='is_eager'
_I='prompt'
_H='expose_value'
_G='callback'
_F='is_flag'
_E='cls'
_D=False
_C=True
_B='help'
_A=None
import inspect,sys
from functools import update_wrapper
from.core import Argument
from.core import Command
from.core import Group
from.core import Option
from.globals import get_current_context
from.utils import echo
def pass_context(f):
	'Marks a callback as wanting to receive the current context\n    object as first argument.\n    '
	def A(*A,**B):return f(get_current_context(),*A,**B)
	return update_wrapper(A,f)
def pass_obj(f):
	'Similar to :func:`pass_context`, but only pass the object on the\n    context onwards (:attr:`Context.obj`).  This is useful if that object\n    represents the state of a nested system.\n    '
	def A(*A,**B):return f(get_current_context().obj,*A,**B)
	return update_wrapper(A,f)
def make_pass_decorator(object_type,ensure=_D):
	"Given an object type this creates a decorator that will work\n    similar to :func:`pass_obj` but instead of passing the object of the\n    current context, it will find the innermost context of type\n    :func:`object_type`.\n\n    This generates a decorator that works roughly like this::\n\n        from functools import update_wrapper\n\n        def decorator(f):\n            @pass_context\n            def new_func(ctx, *args, **kwargs):\n                obj = ctx.find_object(object_type)\n                return ctx.invoke(f, obj, *args, **kwargs)\n            return update_wrapper(new_func, f)\n        return decorator\n\n    :param object_type: the type of the object to pass.\n    :param ensure: if set to `True`, a new object will be created and\n                   remembered on the context if it's not there yet.\n    ";A=object_type
	def B(f):
		def B(*D,**E):
			B=get_current_context()
			if ensure:C=B.ensure_object(A)
			else:C=B.find_object(A)
			if C is _A:raise RuntimeError(f"Managed to invoke callback without a context object of type {A.__name__!r} existing.")
			return B.invoke(f,C,*D,**E)
		return update_wrapper(B,f)
	return B
def _make_command(f,name,attrs,cls):
	A=attrs
	if isinstance(f,Command):raise TypeError('Attempted to convert a callback into a command twice.')
	try:B=f.__click_params__;B.reverse();del f.__click_params__
	except AttributeError:B=[]
	help=A.get(_B)
	if help is _A:
		help=inspect.getdoc(f)
		if isinstance(help,bytes):help=help.decode('utf-8')
	else:help=inspect.cleandoc(help)
	A[_B]=help;return cls(name=name or f.__name__.lower().replace('_','-'),callback=f,params=B,**A)
def command(name=_A,cls=_A,**C):
	'Creates a new :class:`Command` and uses the decorated function as\n    callback.  This will also automatically attach all decorated\n    :func:`option`\\s and :func:`argument`\\s as parameters to the command.\n\n    The name of the command defaults to the name of the function with\n    underscores replaced by dashes.  If you want to change that, you can\n    pass the intended name as the first argument.\n\n    All keyword arguments are forwarded to the underlying command class.\n\n    Once decorated the function turns into a :class:`Command` instance\n    that can be invoked as a command line utility or be attached to a\n    command :class:`Group`.\n\n    :param name: the name of the command.  This defaults to the function\n                 name with underscores replaced by dashes.\n    :param cls: the command class to instantiate.  This defaults to\n                :class:`Command`.\n    ';A=cls
	if A is _A:A=Command
	def B(f):B=_make_command(f,name,C,A);B.__doc__=f.__doc__;return B
	return B
def group(name=_A,**A):'Creates a new :class:`Group` with a function as callback.  This\n    works otherwise the same as :func:`command` just that the `cls`\n    parameter is set to :class:`Group`.\n    ';A.setdefault(_E,Group);return command(name,**A)
def _param_memo(f,param):
	A=param
	if isinstance(f,Command):f.params.append(A)
	else:
		if not hasattr(f,'__click_params__'):f.__click_params__=[]
		f.__click_params__.append(A)
def argument(*B,**A):
	'Attaches an argument to the command.  All positional arguments are\n    passed as parameter declarations to :class:`Argument`; all keyword\n    arguments are forwarded unchanged (except ``cls``).\n    This is equivalent to creating an :class:`Argument` instance manually\n    and attaching it to the :attr:`Command.params` list.\n\n    :param cls: the argument class to instantiate.  This defaults to\n                :class:`Argument`.\n    '
	def C(f):C=A.pop(_E,Argument);_param_memo(f,C(B,**A));return f
	return C
def option(*B,**C):
	'Attaches an option to the command.  All positional arguments are\n    passed as parameter declarations to :class:`Option`; all keyword\n    arguments are forwarded unchanged (except ``cls``).\n    This is equivalent to creating an :class:`Option` instance manually\n    and attaching it to the :attr:`Command.params` list.\n\n    :param cls: the option class to instantiate.  This defaults to\n                :class:`Option`.\n    '
	def A(f):
		A=C.copy()
		if _B in A:A[_B]=inspect.cleandoc(A[_B])
		D=A.pop(_E,Option);_param_memo(f,D(B,**A));return f
	return A
def confirmation_option(*B,**A):
	"Shortcut for confirmation prompts that can be ignored by passing\n    ``--yes`` as parameter.\n\n    This is equivalent to decorating a function with :func:`option` with\n    the following parameters::\n\n        def callback(ctx, param, value):\n            if not value:\n                ctx.abort()\n\n        @click.command()\n        @click.option('--yes', is_flag=True, callback=callback,\n                      expose_value=False, prompt='Do you want to continue?')\n        def dropdb():\n            pass\n    "
	def C(f):
		def C(ctx,param,value):
			if not value:ctx.abort()
		A.setdefault(_F,_C);A.setdefault(_G,C);A.setdefault(_H,_D);A.setdefault(_I,'Do you want to continue?');A.setdefault(_B,'Confirm the action without prompting.');return option(*(B or('--yes',)),**A)(f)
	return C
def password_option(*B,**A):
	"Shortcut for password prompts.\n\n    This is equivalent to decorating a function with :func:`option` with\n    the following parameters::\n\n        @click.command()\n        @click.option('--password', prompt=True, confirmation_prompt=True,\n                      hide_input=True)\n        def changeadmin(password):\n            pass\n    "
	def C(f):A.setdefault(_I,_C);A.setdefault('confirmation_prompt',_C);A.setdefault('hide_input',_C);return option(*(B or('--password',)),**A)(f)
	return C
def version_option(version=_A,*B,**A):
	"Adds a ``--version`` option which immediately ends the program\n    printing out the version number.  This is implemented as an eager\n    option that prints the version and exits the program in the callback.\n\n    :param version: the version number to show.  If not provided Click\n                    attempts an auto discovery via setuptools.\n    :param prog_name: the name of the program (defaults to autodetection)\n    :param message: custom message to show instead of the default\n                    (``'%(prog)s, version %(version)s'``)\n    :param others: everything else is forwarded to :func:`option`.\n    ";D=version
	if D is _A:
		if hasattr(sys,'_getframe'):E=sys._getframe(1).f_globals.get('__name__')
		else:E=''
	def C(f):
		G=A.pop('prog_name',_A);H=A.pop('message','%(prog)s, version %(version)s')
		def C(ctx,param,value):
			A=ctx
			if not value or A.resilient_parsing:return
			C=G
			if C is _A:C=A.find_root().info_name
			B=D
			if B is _A:
				try:import pkg_resources as I
				except ImportError:pass
				else:
					for F in I.working_set:
						J=F.get_entry_map().get('console_scripts')or{}
						for K in J.values():
							if K.module_name==E:B=F.version;break
				if B is _A:raise RuntimeError('Could not determine version')
			echo(H%{'prog':C,'version':B},color=A.color);A.exit()
		A.setdefault(_F,_C);A.setdefault(_H,_D);A.setdefault(_J,_C);A.setdefault(_B,'Show the version and exit.');A[_G]=C;return option(*(B or('--version',)),**A)(f)
	return C
def help_option(*B,**A):
	'Adds a ``--help`` option which immediately ends the program\n    printing out the help page.  This is usually unnecessary to add as\n    this is added by default to all commands unless suppressed.\n\n    Like :func:`version_option`, this is implemented as eager option that\n    prints in the callback and exits.\n\n    All arguments are forwarded to :func:`option`.\n    '
	def C(f):
		def C(ctx,param,value):
			A=ctx
			if value and not A.resilient_parsing:echo(A.get_help(),color=A.color);A.exit()
		A.setdefault(_F,_C);A.setdefault(_H,_D);A.setdefault(_B,'Show this message and exit.');A.setdefault(_J,_C);A[_G]=C;return option(*(B or('--help',)),**A)(f)
	return C
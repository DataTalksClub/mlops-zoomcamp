_C=True
_B=False
_A=None
import inspect,io,itertools,os,struct,sys
from._compat import DEFAULT_COLUMNS,get_winterm_size,isatty,strip_ansi,WIN
from.exceptions import Abort
from.exceptions import UsageError
from.globals import resolve_color_default
from.types import Choice
from.types import convert_type
from.types import Path
from.utils import echo
from.utils import LazyFile
visible_prompt_func=input
_ansi_colors={'black':30,'red':31,'green':32,'yellow':33,'blue':34,'magenta':35,'cyan':36,'white':37,'reset':39,'bright_black':90,'bright_red':91,'bright_green':92,'bright_yellow':93,'bright_blue':94,'bright_magenta':95,'bright_cyan':96,'bright_white':97}
_ansi_reset_all='\x1b[0m'
def hidden_prompt_func(prompt):import getpass as A;return A.getpass(prompt)
def _build_prompt(text,suffix,show_default=_B,default=_A,show_choices=_C,type=_A):
	B=default;A=text
	if type is not _A and show_choices and isinstance(type,Choice):A+=f" ({', '.join(map(str,type.choices))})"
	if B is not _A and show_default:A=f"{A} [{_format_default(B)}]"
	return f"{A}{suffix}"
def _format_default(default):
	A=default
	if isinstance(A,(io.IOBase,LazyFile))and hasattr(A,'name'):return A.name
	return A
def prompt(text,default=_A,hide_input=_B,confirmation_prompt=_B,type=_A,value_proc=_A,prompt_suffix=': ',show_default=_C,err=_B,show_choices=_C):
	F=hide_input;C=err;B=value_proc;A=default;E=_A
	def G(text):
		A=hidden_prompt_func if F else visible_prompt_func
		try:echo(text,nl=_B,err=C);return A('')
		except(KeyboardInterrupt,EOFError):
			if F:echo(_A,err=C)
			raise Abort()
	if B is _A:B=convert_type(type,A)
	I=_build_prompt(text,prompt_suffix,show_default,A,show_choices,type)
	while 1:
		while 1:
			D=G(I)
			if D:break
			elif A is not _A:
				if isinstance(B,Path):D=A;break
				return A
		try:E=B(D)
		except UsageError as J:echo(f"Error: {J.message}",err=C);continue
		if not confirmation_prompt:return E
		while 1:
			H=G('Repeat for confirmation: ')
			if H:break
		if D==H:return E
		echo('Error: the two entered values do not match',err=C)
def confirm(text,default=_B,abort=_B,prompt_suffix=': ',show_default=_C,err=_B):
	C=default;D=_build_prompt(text,prompt_suffix,show_default,'Y/n'if C else'y/N')
	while 1:
		try:echo(D,nl=_B,err=err);B=visible_prompt_func('').lower().strip()
		except(KeyboardInterrupt,EOFError):raise Abort()
		if B in('y','yes'):A=_C
		elif B in('n','no'):A=_B
		elif B=='':A=C
		else:echo('Error: invalid input',err=err);continue
		break
	if abort and not A:raise Abort()
	return A
def get_terminal_size():
	import shutil as C
	if hasattr(C,'get_terminal_size'):return C.get_terminal_size()
	if get_winterm_size is not _A:
		D=get_winterm_size()
		if D==(0,0):return 79,24
		else:return D
	def B(fd):
		try:import fcntl,termios as A;B=struct.unpack('hh',fcntl.ioctl(fd,A.TIOCGWINSZ,'1234'))
		except Exception:return
		return B
	A=B(0)or B(1)or B(2)
	if not A:
		try:
			E=os.open(os.ctermid(),os.O_RDONLY)
			try:A=B(E)
			finally:os.close(E)
		except Exception:pass
	if not A or not A[0]or not A[1]:A=os.environ.get('LINES',25),os.environ.get('COLUMNS',DEFAULT_COLUMNS)
	return int(A[1]),int(A[0])
def echo_via_pager(text_or_generator,color=_A):
	B=color;A=text_or_generator;B=resolve_color_default(B)
	if inspect.isgeneratorfunction(A):C=A()
	elif isinstance(A,str):C=[A]
	else:C=iter(A)
	D=(A if isinstance(A,str)else str(A)for A in C);from._termui_impl import pager;return pager(itertools.chain(D,'\n'),B)
def progressbar(iterable=_A,length=_A,label=_A,show_eta=_C,show_percent=_A,show_pos=_B,item_show_func=_A,fill_char='#',empty_char='-',bar_template='%(label)s  [%(bar)s]  %(info)s',info_sep='  ',width=36,file=_A,color=_A):A=color;from._termui_impl import ProgressBar as B;A=resolve_color_default(A);return B(iterable=iterable,length=length,show_eta=show_eta,show_percent=show_percent,show_pos=show_pos,item_show_func=item_show_func,fill_char=fill_char,empty_char=empty_char,bar_template=bar_template,info_sep=info_sep,file=file,label=label,width=width,color=A)
def clear():
	if not isatty(sys.stdout):return
	if WIN:os.system('cls')
	else:sys.stdout.write('\x1b[2J\x1b[1;1H')
def style(text,fg=_A,bg=_A,bold=_A,dim=_A,underline=_A,blink=_A,reverse=_A,reset=_C):
	D=reverse;C=blink;B=underline;A=[]
	if fg:
		try:A.append(f"[{_ansi_colors[fg]}m")
		except KeyError:raise TypeError(f"Unknown color {fg!r}")
	if bg:
		try:A.append(f"[{_ansi_colors[bg]+10}m")
		except KeyError:raise TypeError(f"Unknown color {bg!r}")
	if bold is not _A:A.append(f"[{1 if bold else 22}m")
	if dim is not _A:A.append(f"[{2 if dim else 22}m")
	if B is not _A:A.append(f"[{4 if B else 24}m")
	if C is not _A:A.append(f"[{5 if C else 25}m")
	if D is not _A:A.append(f"[{7 if D else 27}m")
	A.append(text)
	if reset:A.append(_ansi_reset_all)
	return''.join(A)
def unstyle(text):return strip_ansi(text)
def secho(message=_A,file=_A,nl=_C,err=_B,color=_A,**B):
	A=message
	if A is not _A:A=style(A,**B)
	return echo(A,file=file,nl=nl,err=err,color=color)
def edit(text=_A,editor=_A,env=_A,require_save=_C,extension='.txt',filename=_A):
	B=filename;A=editor;from._termui_impl import Editor as C;A=C(editor=A,env=env,require_save=require_save,extension=extension)
	if B is _A:return A.edit(text)
	A.edit_file(B)
def launch(url,wait=_B,locate=_B):from._termui_impl import open_url as A;return A(url,wait=wait,locate=locate)
_getchar=_A
def getchar(echo=_B):
	A=_getchar
	if A is _A:from._termui_impl import getchar as A
	return A(echo)
def raw_terminal():from._termui_impl import raw_terminal as A;return A()
def pause(info='Press any key to continue ...',err=_B):
	A=info
	if not isatty(sys.stdin)or not isatty(sys.stdout):return
	try:
		if A:echo(A,nl=_B,err=err)
		try:getchar()
		except(KeyboardInterrupt,EOFError):pass
	finally:
		if A:echo(err=err)
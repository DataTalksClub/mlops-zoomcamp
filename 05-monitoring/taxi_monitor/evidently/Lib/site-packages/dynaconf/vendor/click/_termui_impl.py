_F='replace'
_E='You need to use progress bars in a with block.'
_D='\n'
_C=False
_B=True
_A=None
import contextlib,math,os,sys,time
from._compat import _default_text_stdout,CYGWIN,get_best_encoding,isatty,open_stream,strip_ansi,term_len,WIN
from.exceptions import ClickException
from.utils import echo
if os.name=='nt':BEFORE_BAR='\r';AFTER_BAR=_D
else:BEFORE_BAR='\r\x1b[?25l';AFTER_BAR='\x1b[?25h\n'
def _length_hint(obj):
	B=obj
	try:return len(B)
	except(AttributeError,TypeError):
		try:C=type(B).__length_hint__
		except AttributeError:return
		try:A=C(B)
		except TypeError:return
		if A is NotImplemented or not isinstance(A,int)or A<0:return
		return A
class ProgressBar:
	def __init__(A,iterable,length=_A,fill_char='#',empty_char=' ',bar_template='%(bar)s',info_sep='  ',show_eta=_B,show_percent=_A,show_pos=_C,item_show_func=_A,label=_A,file=_A,color=_A,width=30):
		E=width;D=file;C=iterable;B=length;A.fill_char=fill_char;A.empty_char=empty_char;A.bar_template=bar_template;A.info_sep=info_sep;A.show_eta=show_eta;A.show_percent=show_percent;A.show_pos=show_pos;A.item_show_func=item_show_func;A.label=label or''
		if D is _A:D=_default_text_stdout()
		A.file=D;A.color=color;A.width=E;A.autowidth=E==0
		if B is _A:B=_length_hint(C)
		if C is _A:
			if B is _A:raise TypeError('iterable or length is required')
			C=range(B)
		A.iter=iter(C);A.length=B;A.length_known=B is not _A;A.pos=0;A.avg=[];A.start=A.last_eta=time.time();A.eta_known=_C;A.finished=_C;A.max_width=_A;A.entered=_C;A.current_item=_A;A.is_hidden=not isatty(A.file);A._last_line=_A;A.short_limit=.5
	def __enter__(A):A.entered=_B;A.render_progress();return A
	def __exit__(A,exc_type,exc_value,tb):A.render_finish()
	def __iter__(A):
		if not A.entered:raise RuntimeError(_E)
		A.render_progress();return A.generator()
	def __next__(A):return next(iter(A))
	def is_fast(A):return time.time()-A.start<=A.short_limit
	def render_finish(A):
		if A.is_hidden or A.is_fast():return
		A.file.write(AFTER_BAR);A.file.flush()
	@property
	def pct(self):
		A=self
		if A.finished:return 1.
		return min(A.pos/(float(A.length)or 1),1.)
	@property
	def time_per_iteration(self):
		A=self
		if not A.avg:return .0
		return sum(A.avg)/float(len(A.avg))
	@property
	def eta(self):
		A=self
		if A.length_known and not A.finished:return A.time_per_iteration*(A.length-A.pos)
		return .0
	def format_eta(B):
		if B.eta_known:
			A=int(B.eta);C=A%60;A//=60;D=A%60;A//=60;E=A%24;A//=24
			if A>0:return f"{A}d {E:02}:{D:02}:{C:02}"
			else:return f"{E:02}:{D:02}:{C:02}"
		return''
	def format_pos(A):
		B=str(A.pos)
		if A.length_known:B+=f"/{A.length}"
		return B
	def format_pct(A):return f"{int(A.pct*100): 4}%"[1:]
	def format_bar(A):
		if A.length_known:C=int(A.pct*A.width);B=A.fill_char*C;B+=A.empty_char*(A.width-C)
		elif A.finished:B=A.fill_char*A.width
		else:
			B=list(A.empty_char*(A.width or 1))
			if A.time_per_iteration!=0:B[int((math.cos(A.pos*A.time_per_iteration)/2.+.5)*A.width)]=A.fill_char
			B=''.join(B)
		return B
	def format_progress_line(A):
		C=A.show_percent;B=[]
		if A.length_known and C is _A:C=not A.show_pos
		if A.show_pos:B.append(A.format_pos())
		if C:B.append(A.format_pct())
		if A.show_eta and A.eta_known and not A.finished:B.append(A.format_eta())
		if A.item_show_func is not _A:
			D=A.item_show_func(A.current_item)
			if D is not _A:B.append(D)
		return(A.bar_template%{'label':A.label,'bar':A.format_bar(),'info':A.info_sep.join(B)}).rstrip()
	def render_progress(A):
		from.termui import get_terminal_size as G
		if A.is_hidden:return
		B=[]
		if A.autowidth:
			H=A.width;A.width=0;I=term_len(A.format_progress_line());D=max(0,G()[0]-I)
			if D<H:B.append(BEFORE_BAR);B.append(' '*A.max_width);A.max_width=D
			A.width=D
		F=A.width
		if A.max_width is not _A:F=A.max_width
		B.append(BEFORE_BAR);C=A.format_progress_line();E=term_len(C)
		if A.max_width is _A or A.max_width<E:A.max_width=E
		B.append(C);B.append(' '*(F-E));C=''.join(B)
		if C!=A._last_line and not A.is_fast():A._last_line=C;echo(C,file=A.file,color=A.color,nl=_C);A.file.flush()
	def make_step(A,n_steps):
		A.pos+=n_steps
		if A.length_known and A.pos>=A.length:A.finished=_B
		if time.time()-A.last_eta<1.:return
		A.last_eta=time.time()
		if A.pos:B=(time.time()-A.start)/A.pos
		else:B=time.time()-A.start
		A.avg=A.avg[-6:]+[B];A.eta_known=A.length_known
	def update(A,n_steps,current_item=_A):
		B=current_item;A.make_step(n_steps)
		if B is not _A:A.current_item=B
		A.render_progress()
	def finish(A):A.eta_known=0;A.current_item=_A;A.finished=_B
	def generator(A):
		if not A.entered:raise RuntimeError(_E)
		if A.is_hidden:yield from A.iter
		else:
			for B in A.iter:A.current_item=B;yield B;A.update(1)
			A.finish();A.render_progress()
def pager(generator,color=_A):
	F='system';B=color;A=generator;C=_default_text_stdout()
	if not isatty(sys.stdin)or not isatty(C):return _nullpager(C,A,B)
	D=(os.environ.get('PAGER',_A)or'').strip()
	if D:
		if WIN:return _tempfilepager(A,D,B)
		return _pipepager(A,D,B)
	if os.environ.get('TERM')in('dumb','emacs'):return _nullpager(C,A,B)
	if WIN or sys.platform.startswith('os2'):return _tempfilepager(A,'more <',B)
	if hasattr(os,F)and os.system('(less) 2>/dev/null')==0:return _pipepager(A,'less',B)
	import tempfile as G;H,E=G.mkstemp();os.close(H)
	try:
		if hasattr(os,F)and os.system(f'more "{E}"')==0:return _pipepager(A,'more',B)
		return _nullpager(C,A,B)
	finally:os.unlink(E)
def _pipepager(generator,cmd,color):
	H='LESS';A=color;import subprocess as E;F=dict(os.environ);G=cmd.rsplit('/',1)[-1].split()
	if A is _A and G[0]=='less':
		C=f"{os.environ.get(H,'')}{' '.join(G[1:])}"
		if not C:F[H]='-R';A=_B
		elif'r'in C or'R'in C:A=_B
	B=E.Popen(cmd,shell=_B,stdin=E.PIPE,env=F);I=get_best_encoding(B.stdin)
	try:
		for D in generator:
			if not A:D=strip_ansi(D)
			B.stdin.write(D.encode(I,_F))
	except(OSError,KeyboardInterrupt):pass
	else:B.stdin.close()
	while _B:
		try:B.wait()
		except KeyboardInterrupt:pass
		else:break
def _tempfilepager(generator,cmd,color):
	import tempfile as C;A=C.mktemp();B=''.join(generator)
	if not color:B=strip_ansi(B)
	D=get_best_encoding(sys.stdout)
	with open_stream(A,'wb')[0]as E:E.write(B.encode(D))
	try:os.system(f'{cmd} "{A}"')
	finally:os.unlink(A)
def _nullpager(stream,generator,color):
	for A in generator:
		if not color:A=strip_ansi(A)
		stream.write(A)
class Editor:
	def __init__(A,editor=_A,env=_A,require_save=_B,extension='.txt'):A.editor=editor;A.env=env;A.require_save=require_save;A.extension=extension
	def get_editor(A):
		if A.editor is not _A:return A.editor
		for D in('VISUAL','EDITOR'):
			B=os.environ.get(D)
			if B:return B
		if WIN:return'notepad'
		for C in('sensible-editor','vim','nano'):
			if os.system(f"which {C} >/dev/null 2>&1")==0:return C
		return'vi'
	def edit_file(A,filename):
		import subprocess as D;B=A.get_editor()
		if A.env:C=os.environ.copy();C.update(A.env)
		else:C=_A
		try:
			E=D.Popen(f'{B} "{filename}"',env=C,shell=_B);F=E.wait()
			if F!=0:raise ClickException(f"{B}: Editing failed!")
		except OSError as G:raise ClickException(f"{B}: Editing failed: {G}")
	def edit(D,text):
		I='\r\n';H='utf-8-sig';A=text;import tempfile as J;A=A or'';E=type(A)in[bytes,bytearray]
		if not E and A and not A.endswith(_D):A+=_D
		K,B=J.mkstemp(prefix='editor-',suffix=D.extension)
		try:
			if not E:
				if WIN:F=H;A=A.replace(_D,I)
				else:F='utf-8'
				A=A.encode(F)
			C=os.fdopen(K,'wb');C.write(A);C.close();L=os.path.getmtime(B);D.edit_file(B)
			if D.require_save and os.path.getmtime(B)==L:return
			C=open(B,'rb')
			try:G=C.read()
			finally:C.close()
			if E:return G
			else:return G.decode(H).replace(I,_D)
		finally:os.unlink(B)
def open_url(url,wait=_C,locate=_C):
	F='"';D=locate;C=wait;A=url;import subprocess as G
	def E(url):
		A=url;import urllib as B
		if A.startswith('file://'):A=B.unquote(A[7:])
		return A
	if sys.platform=='darwin':
		B=['open']
		if C:B.append('-W')
		if D:B.append('-R')
		B.append(E(A));H=open('/dev/null','w')
		try:return G.Popen(B,stderr=H).wait()
		finally:H.close()
	elif WIN:
		if D:A=E(A.replace(F,''));B=f'explorer /select,"{A}"'
		else:A=A.replace(F,'');C='/WAIT'if C else'';B=f'start {C} "" "{A}"'
		return os.system(B)
	elif CYGWIN:
		if D:A=os.path.dirname(E(A).replace(F,''));B=f'cygstart "{A}"'
		else:A=A.replace(F,'');C='-w'if C else'';B=f'cygstart {C} "{A}"'
		return os.system(B)
	try:
		if D:A=os.path.dirname(E(A))or'.'
		else:A=E(A)
		I=G.Popen(['xdg-open',A])
		if C:return I.wait()
		return 0
	except OSError:
		if A.startswith(('http://','https://'))and not D and not C:import webbrowser as J;J.open(A);return 0
		return 1
def _translate_ch_to_exc(ch):
	if ch=='\x03':raise KeyboardInterrupt()
	if ch=='\x04'and not WIN:raise EOFError()
	if ch=='\x1a'and WIN:raise EOFError()
if WIN:
	import msvcrt
	@contextlib.contextmanager
	def raw_terminal():yield
	def getchar(echo):
		if echo:B=msvcrt.getwche
		else:B=msvcrt.getwch
		A=B()
		if A in('\x00','à'):A+=B()
		_translate_ch_to_exc(A);return A
else:
	import tty,termios
	@contextlib.contextmanager
	def raw_terminal():
		if not isatty(sys.stdin):B=open('/dev/tty');A=B.fileno()
		else:A=sys.stdin.fileno();B=_A
		try:
			C=termios.tcgetattr(A)
			try:tty.setraw(A);yield A
			finally:
				termios.tcsetattr(A,termios.TCSADRAIN,C);sys.stdout.flush()
				if B is not _A:B.close()
		except termios.error:pass
	def getchar(echo):
		with raw_terminal()as B:
			A=os.read(B,32);A=A.decode(get_best_encoding(sys.stdin),_F)
			if echo and isatty(sys.stdout):sys.stdout.write(A)
			_translate_ch_to_exc(A);return A
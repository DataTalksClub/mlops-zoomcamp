_D='replace'
_C=False
_B='\r\n'
_A=None
import contextlib,io,os,shlex,shutil,sys,tempfile
from.import formatting,termui,utils
from._compat import _find_binary_reader
class EchoingStdin:
	def __init__(A,input,output):A._input=input;A._output=output
	def __getattr__(A,x):return getattr(A._input,x)
	def _echo(A,rv):A._output.write(rv);return rv
	def read(A,n=-1):return A._echo(A._input.read(n))
	def readline(A,n=-1):return A._echo(A._input.readline(n))
	def readlines(A):return[A._echo(B)for B in A._input.readlines()]
	def __iter__(A):return iter(A._echo(B)for B in A._input)
	def __repr__(A):return repr(A._input)
def make_input_stream(input,charset):
	if hasattr(input,'read'):
		A=_find_binary_reader(input)
		if A is not _A:return A
		raise TypeError('Could not find binary reader for input stream.')
	if input is _A:input=b''
	elif not isinstance(input,bytes):input=input.encode(charset)
	return io.BytesIO(input)
class Result:
	def __init__(A,runner,stdout_bytes,stderr_bytes,exit_code,exception,exc_info=_A):A.runner=runner;A.stdout_bytes=stdout_bytes;A.stderr_bytes=stderr_bytes;A.exit_code=exit_code;A.exception=exception;A.exc_info=exc_info
	@property
	def output(self):return self.stdout
	@property
	def stdout(self):return self.stdout_bytes.decode(self.runner.charset,_D).replace(_B,'\n')
	@property
	def stderr(self):
		A=self
		if A.stderr_bytes is _A:raise ValueError('stderr not separately captured')
		return A.stderr_bytes.decode(A.runner.charset,_D).replace(_B,'\n')
	def __repr__(A):B=repr(A.exception)if A.exception else'okay';return f"<{type(A).__name__} {B}>"
class CliRunner:
	def __init__(A,charset='utf-8',env=_A,echo_stdin=_C,mix_stderr=True):A.charset=charset;A.env=env or{};A.echo_stdin=echo_stdin;A.mix_stderr=mix_stderr
	def get_default_prog_name(A,cli):return cli.name or'root'
	def make_env(C,overrides=_A):
		A=overrides;B=dict(C.env)
		if A:B.update(A)
		return B
	@contextlib.contextmanager
	def isolation(self,input=_A,env=_A,color=_C):
		D=env;A=self;input=make_input_stream(input,A.charset);H=sys.stdin;I=sys.stdout;J=sys.stderr;K=formatting.FORCED_WIDTH;formatting.FORCED_WIDTH=80;D=A.make_env(D);E=io.BytesIO()
		if A.echo_stdin:input=EchoingStdin(input,E)
		input=io.TextIOWrapper(input,encoding=A.charset);sys.stdout=io.TextIOWrapper(E,encoding=A.charset)
		if not A.mix_stderr:F=io.BytesIO();sys.stderr=io.TextIOWrapper(F,encoding=A.charset)
		if A.mix_stderr:sys.stderr=sys.stdout
		sys.stdin=input
		def L(prompt=_A):sys.stdout.write(prompt or'');A=input.readline().rstrip(_B);sys.stdout.write(f"{A}\n");sys.stdout.flush();return A
		def M(prompt=_A):sys.stdout.write(f"{prompt or''}\n");sys.stdout.flush();return input.readline().rstrip(_B)
		def N(echo):
			A=sys.stdin.read(1)
			if echo:sys.stdout.write(A);sys.stdout.flush()
			return A
		O=color
		def P(stream=_A,color=_A):
			A=color
			if A is _A:return not O
			return not A
		Q=termui.visible_prompt_func;R=termui.hidden_prompt_func;S=termui._getchar;T=utils.should_strip_ansi;termui.visible_prompt_func=L;termui.hidden_prompt_func=M;termui._getchar=N;utils.should_strip_ansi=P;G={}
		try:
			for(B,C)in D.items():
				G[B]=os.environ.get(B)
				if C is _A:
					try:del os.environ[B]
					except Exception:pass
				else:os.environ[B]=C
			yield(E,not A.mix_stderr and F)
		finally:
			for(B,C)in G.items():
				if C is _A:
					try:del os.environ[B]
					except Exception:pass
				else:os.environ[B]=C
			sys.stdout=I;sys.stderr=J;sys.stdin=H;termui.visible_prompt_func=Q;termui.hidden_prompt_func=R;termui._getchar=S;utils.should_strip_ansi=T;formatting.FORCED_WIDTH=K
	def invoke(B,cli,args=_A,input=_A,env=_A,catch_exceptions=True,color=_C,**G):
		C=args;E=_A
		with B.isolation(input=input,env=env,color=color)as H:
			F=_A;A=0
			if isinstance(C,str):C=shlex.split(C)
			try:I=G.pop('prog_name')
			except KeyError:I=B.get_default_prog_name(cli)
			try:cli.main(args=C or(),prog_name=I,**G)
			except SystemExit as D:
				E=sys.exc_info();A=D.code
				if A is _A:A=0
				if A!=0:F=D
				if not isinstance(A,int):sys.stdout.write(str(A));sys.stdout.write('\n');A=1
			except Exception as D:
				if not catch_exceptions:raise
				F=D;A=1;E=sys.exc_info()
			finally:
				sys.stdout.flush();K=H[0].getvalue()
				if B.mix_stderr:J=_A
				else:J=H[1].getvalue()
		return Result(runner=B,stdout_bytes=K,stderr_bytes=J,exit_code=A,exception=F,exc_info=E)
	@contextlib.contextmanager
	def isolated_filesystem(self):
		B=os.getcwd();A=tempfile.mkdtemp();os.chdir(A)
		try:yield A
		finally:
			os.chdir(B)
			try:shutil.rmtree(A)
			except OSError:pass
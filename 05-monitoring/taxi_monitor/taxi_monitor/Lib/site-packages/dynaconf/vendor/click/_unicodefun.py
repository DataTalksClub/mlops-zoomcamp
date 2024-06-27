import codecs,os
def _verify_python_env():
	L='.utf8';K='.utf-8';H=None;G='ascii'
	try:import locale as A;I=codecs.lookup(A.getpreferredencoding()).name
	except Exception:I=G
	if I!=G:return
	B=''
	if os.name=='posix':
		import subprocess as D
		try:C=D.Popen(['locale','-a'],stdout=D.PIPE,stderr=D.PIPE).communicate()[0]
		except OSError:C=b''
		E=set();J=False
		if isinstance(C,bytes):C=C.decode(G,'replace')
		for M in C.splitlines():
			A=M.strip()
			if A.lower().endswith((K,L)):
				E.add(A)
				if A.lower()in('c.utf8','c.utf-8'):J=True
		B+='\n\n'
		if not E:B+='Additional information: on this system no suitable UTF-8 locales were discovered. This most likely requires resolving by reconfiguring the locale system.'
		elif J:B+='This system supports the C.UTF-8 locale which is recommended. You might be able to resolve your issue by exporting the following environment variables:\n\n    export LC_ALL=C.UTF-8\n    export LANG=C.UTF-8'
		else:B+=f"This system lists some UTF-8 supporting locales that you can pick from. The following suitable locales were discovered: {', '.join(sorted(E))}"
		F=H
		for A in(os.environ.get('LC_ALL'),os.environ.get('LANG')):
			if A and A.lower().endswith((K,L)):F=A
			if A is not H:break
		if F is not H:B+=f"\n\nClick discovered that you exported a UTF-8 locale but the locale system could not pick up from it because it does not exist. The exported locale is {F!r} but it is not supported"
	raise RuntimeError(f"Click will abort further execution because Python was configured to use ASCII as encoding for the environment. Consult https://click.palletsprojects.com/unicode-support/ for mitigation steps.{B}")
from threading import local
_local=local()
def get_current_context(silent=False):
	try:return _local.stack[-1]
	except(AttributeError,IndexError):
		if not silent:raise RuntimeError('There is no active click context.')
def push_context(ctx):_local.__dict__.setdefault('stack',[]).append(ctx)
def pop_context():_local.stack.pop()
def resolve_color_default(color=None):
	A=color
	if A is not None:return A
	B=get_current_context(silent=True)
	if B is not None:return B.color
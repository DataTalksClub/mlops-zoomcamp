_F='always'
_E='key'
_D='%s=%s'
_C='QUOTE'
_B='FILE'
_A=True
import os,sys
from subprocess import Popen
try:from dynaconf.vendor import click
except ImportError:sys.stderr.write('It seems python-dotenv is not installed with cli option. \nRun pip install "python-dotenv[cli]" to fix this.');sys.exit(1)
from.compat import IS_TYPE_CHECKING,to_env
from.main import dotenv_values,get_key,set_key,unset_key
from.version import __version__
if IS_TYPE_CHECKING:from typing import Any,List,Dict
@click.group()
@click.option('-f','--file',default=os.path.join(os.getcwd(),'.env'),type=click.Path(exists=_A),help='Location of the .env file, defaults to .env file in current working directory.')
@click.option('-q','--quote',default=_F,type=click.Choice([_F,'never','auto']),help='Whether to quote or not the variable values. Default mode is always. This does not affect parsing.')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx,file,quote):A=ctx;A.obj={};A.obj[_B]=file;A.obj[_C]=quote
@cli.command()
@click.pass_context
def list(ctx):
	A=ctx.obj[_B];B=dotenv_values(A)
	for(C,D)in B.items():click.echo(_D%(C,D))
@cli.command()
@click.pass_context
@click.argument(_E,required=_A)
@click.argument('value',required=_A)
def set(ctx,key,value):
	B=value;A=key;C=ctx.obj[_B];D=ctx.obj[_C];E,A,B=set_key(C,A,B,D)
	if E:click.echo(_D%(A,B))
	else:exit(1)
@cli.command()
@click.pass_context
@click.argument(_E,required=_A)
def get(ctx,key):
	B=ctx.obj[_B];A=get_key(B,key)
	if A:click.echo(_D%(key,A))
	else:exit(1)
@cli.command()
@click.pass_context
@click.argument(_E,required=_A)
def unset(ctx,key):
	A=key;B=ctx.obj[_B];C=ctx.obj[_C];D,A=unset_key(B,A,C)
	if D:click.echo('Successfully removed %s'%A)
	else:exit(1)
@cli.command(context_settings={'ignore_unknown_options':_A})
@click.pass_context
@click.argument('commandline',nargs=-1,type=click.UNPROCESSED)
def run(ctx,commandline):
	A=commandline;B=ctx.obj[_B];C={to_env(B):to_env(A)for(B,A)in dotenv_values(B).items()if A is not None}
	if not A:click.echo('No command given.');exit(1)
	D=run_command(A,C);exit(D)
def run_command(command,env):A=os.environ.copy();A.update(env);B=Popen(command,universal_newlines=_A,bufsize=0,shell=False,env=A);C,C=B.communicate();return B.returncode
if __name__=='__main__':cli()
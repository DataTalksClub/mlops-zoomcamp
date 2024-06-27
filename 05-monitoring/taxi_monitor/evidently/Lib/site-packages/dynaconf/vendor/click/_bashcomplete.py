_G='COMP_CWORD'
_F='COMP_WORDS'
_E='zsh'
_D='bash'
_C=False
_B=None
_A=True
import copy,os,re
from collections import abc
from.core import Argument
from.core import MultiCommand
from.core import Option
from.parser import split_arg_string
from.types import Choice
from.utils import echo
WORDBREAK='='
COMPLETION_SCRIPT_BASH='\n%(complete_func)s() {\n    local IFS=$\'\n\'\n    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \\\n                   COMP_CWORD=$COMP_CWORD \\\n                   %(autocomplete_var)s=complete $1 ) )\n    return 0\n}\n\n%(complete_func)setup() {\n    local COMPLETION_OPTIONS=""\n    local BASH_VERSION_ARR=(${BASH_VERSION//./ })\n    # Only BASH version 4.4 and later have the nosort option.\n    if [ ${BASH_VERSION_ARR[0]} -gt 4 ] || ([ ${BASH_VERSION_ARR[0]} -eq 4 ] && [ ${BASH_VERSION_ARR[1]} -ge 4 ]); then\n        COMPLETION_OPTIONS="-o nosort"\n    fi\n\n    complete $COMPLETION_OPTIONS -F %(complete_func)s %(script_names)s\n}\n\n%(complete_func)setup\n'
COMPLETION_SCRIPT_ZSH='\n#compdef %(script_names)s\n\n%(complete_func)s() {\n    local -a completions\n    local -a completions_with_descriptions\n    local -a response\n    (( ! $+commands[%(script_names)s] )) && return 1\n\n    response=("${(@f)$( env COMP_WORDS="${words[*]}" \\\n                        COMP_CWORD=$((CURRENT-1)) \\\n                        %(autocomplete_var)s="complete_zsh" \\\n                        %(script_names)s )}")\n\n    for key descr in ${(kv)response}; do\n      if [[ "$descr" == "_" ]]; then\n          completions+=("$key")\n      else\n          completions_with_descriptions+=("$key":"$descr")\n      fi\n    done\n\n    if [ -n "$completions_with_descriptions" ]; then\n        _describe -V unsorted completions_with_descriptions -U\n    fi\n\n    if [ -n "$completions" ]; then\n        compadd -U -V unsorted -a completions\n    fi\n    compstate[insert]="automenu"\n}\n\ncompdef %(complete_func)s %(script_names)s\n'
COMPLETION_SCRIPT_FISH='complete --no-files --command %(script_names)s --arguments "(env %(autocomplete_var)s=complete_fish COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) %(script_names)s)"'
_completion_scripts={_D:COMPLETION_SCRIPT_BASH,_E:COMPLETION_SCRIPT_ZSH,'fish':COMPLETION_SCRIPT_FISH}
_invalid_ident_char_re=re.compile('[^a-zA-Z0-9_]')
def get_completion_script(prog_name,complete_var,shell):A=prog_name;B=_invalid_ident_char_re.sub('',A.replace('-','_'));C=_completion_scripts.get(shell,COMPLETION_SCRIPT_BASH);return(C%{'complete_func':f"_{B}_completion",'script_names':A,'autocomplete_var':complete_var}).strip()+';'
def resolve_ctx(cli,prog_name,args):
	B=args;A=cli.make_context(prog_name,B,resilient_parsing=_A);B=A.protected_args+A.args
	while B:
		if isinstance(A.command,MultiCommand):
			if not A.command.chain:
				E,C,B=A.command.resolve_command(A,B)
				if C is _B:return A
				A=C.make_context(E,B,parent=A,resilient_parsing=_A);B=A.protected_args+A.args
			else:
				while B:
					E,C,B=A.command.resolve_command(A,B)
					if C is _B:return A
					D=C.make_context(E,B,parent=A,allow_extra_args=_A,allow_interspersed_args=_C,resilient_parsing=_A);B=D.args
				A=D;B=D.protected_args+D.args
		else:break
	return A
def start_of_option(param_str):A=param_str;return A and A[:1]=='-'
def is_incomplete_option(all_args,cmd_param):
	A=cmd_param
	if not isinstance(A,Option):return _C
	if A.is_flag:return _C
	B=_B
	for(D,C)in enumerate(reversed([A for A in all_args if A!=WORDBREAK])):
		if D+1>A.nargs:break
		if start_of_option(C):B=C
	return _A if B and B in A.opts else _C
def is_incomplete_argument(current_params,cmd_param):
	A=cmd_param
	if not isinstance(A,Argument):return _C
	B=current_params[A.name]
	if B is _B:return _A
	if A.nargs==-1:return _A
	if isinstance(B,abc.Iterable)and A.nargs>1 and len(B)<A.nargs:return _A
	return _C
def get_user_autocompletions(ctx,args,incomplete,cmd_param):
	C=incomplete;A=cmd_param;B=[]
	if isinstance(A.type,Choice):B=[(A,_B)for A in A.type.choices if str(A).startswith(C)]
	elif A.autocompletion is not _B:D=A.autocompletion(ctx=ctx,args=args,incomplete=C);B=[A if isinstance(A,tuple)else(A,_B)for A in D]
	return B
def get_visible_commands_starting_with(ctx,starts_with):
	A=ctx
	for B in A.command.list_commands(A):
		if B.startswith(starts_with):
			C=A.command.get_command(A,B)
			if not C.hidden:yield C
def add_subcommand_completions(ctx,incomplete,completions_out):
	C=completions_out;B=incomplete;A=ctx
	if isinstance(A.command,MultiCommand):C.extend([(A.name,A.get_short_help_str())for A in get_visible_commands_starting_with(A,B)])
	while A.parent is not _B:
		A=A.parent
		if isinstance(A.command,MultiCommand)and A.command.chain:D=[B for B in get_visible_commands_starting_with(A,B)if B.name not in A.protected_args];C.extend([(A.name,A.get_short_help_str())for A in D])
def get_choices(cli,prog_name,args,incomplete):
	B=incomplete;D=copy.deepcopy(args);C=resolve_ctx(cli,prog_name,args)
	if C is _B:return[]
	G='--'in D
	if start_of_option(B)and WORDBREAK in B:F=B.partition(WORDBREAK);D.append(F[0]);B=F[2]
	elif B==WORDBREAK:B=''
	E=[]
	if not G and start_of_option(B):
		for A in C.command.params:
			if isinstance(A,Option)and not A.hidden:H=[B for B in A.opts+A.secondary_opts if B not in D or A.multiple];E.extend([(C,A.help)for C in H if C.startswith(B)])
		return E
	for A in C.command.params:
		if is_incomplete_option(D,A):return get_user_autocompletions(C,D,B,A)
	for A in C.command.params:
		if is_incomplete_argument(C.params,A):return get_user_autocompletions(C,D,B,A)
	add_subcommand_completions(C,B,E);return sorted(E)
def do_complete(cli,prog_name,include_descriptions):
	B=split_arg_string(os.environ[_F]);C=int(os.environ[_G]);E=B[1:C]
	try:D=B[C]
	except IndexError:D=''
	for A in get_choices(cli,prog_name,E,D):
		echo(A[0])
		if include_descriptions:echo(A[1]if A[1]else'_')
	return _A
def do_complete_fish(cli,prog_name):
	B=split_arg_string(os.environ[_F]);C=os.environ[_G];D=B[1:]
	for A in get_choices(cli,prog_name,D,C):
		if A[1]:echo(f"{A[0]}\t{A[1]}")
		else:echo(A[0])
	return _A
def bashcomplete(cli,prog_name,complete_var,complete_instr):
	C=complete_instr;B=prog_name
	if'_'in C:D,A=C.split('_',1)
	else:D=C;A=_D
	if D=='source':echo(get_completion_script(B,complete_var,A));return _A
	elif D=='complete':
		if A=='fish':return do_complete_fish(cli,B)
		elif A in{_D,_E}:return do_complete(cli,B,A==_E)
	return _C
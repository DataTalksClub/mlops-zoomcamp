from __future__ import print_function,absolute_import,division,unicode_literals
_T='bdist_wheel'
_S='--version'
_R='extra_packages'
_Q='universal'
_P='nested'
_O='setting  distdir {}/{}'
_N='PYDISTBASE'
_M='DVDEBUG'
_L='LICENSE'
_K='Jython'
_J='install'
_I='full_package_name'
_H='__init__.py'
_G='python'
_F='setup.py'
_E='utf-8'
_D=True
_C=False
_B='.'
_A=None
import sys,os,datetime,traceback
sys.path=[path for path in sys.path if path not in[os.getcwd(),'']]
import platform
from _ast import*
from ast import parse
from setuptools import setup,Extension,Distribution
from setuptools.command import install_lib
from setuptools.command.sdist import sdist as _sdist
try:from setuptools.namespaces import Installer as NameSpaceInstaller
except ImportError:msg='You should use the latest setuptools. The namespaces.py file that this setup.py uses was added in setuptools 28.7.0 (Oct 2016)';print(msg);sys.exit()
if __name__!='__main__':raise NotImplementedError('should never include setup.py')
full_package_name=_A
if sys.version_info<(3,):string_type=basestring
else:string_type=str
if sys.version_info<(3,4):
	class Bytes:0
	class NameConstant:0
if sys.version_info>=(3,8):from ast import Str,Num,Bytes,NameConstant
if sys.version_info<(3,):open_kw=dict()
else:open_kw=dict(encoding=_E)
if sys.version_info<(2,7)or platform.python_implementation()==_K:
	class Set:0
if os.environ.get(_M,'')=='':
	def debug(*args,**kw):0
else:
	def debug(*args,**kw):
		with open(os.environ[_M],'a')as fp:kw1=kw.copy();kw1['file']=fp;print('{:%Y-%d-%mT%H:%M:%S}'.format(datetime.datetime.now()),file=fp,end=' ');print(*args,**kw1)
def literal_eval(node_or_string):
	_safe_names={'None':_A,'True':_D,'False':_C}
	if isinstance(node_or_string,string_type):node_or_string=parse(node_or_string,mode='eval')
	if isinstance(node_or_string,Expression):node_or_string=node_or_string.body
	else:raise TypeError('only string or AST nodes supported')
	def _convert(node):
		if isinstance(node,Str):
			if sys.version_info<(3,)and not isinstance(node.s,unicode):return node.s.decode(_E)
			return node.s
		elif isinstance(node,Bytes):return node.s
		elif isinstance(node,Num):return node.n
		elif isinstance(node,Tuple):return tuple(map(_convert,node.elts))
		elif isinstance(node,List):return list(map(_convert,node.elts))
		elif isinstance(node,Set):return set(map(_convert,node.elts))
		elif isinstance(node,Dict):return dict((_convert(k),_convert(v))for(k,v)in zip(node.keys,node.values))
		elif isinstance(node,NameConstant):return node.value
		elif sys.version_info<(3,4)and isinstance(node,Name):
			if node.id in _safe_names:return _safe_names[node.id]
		elif isinstance(node,UnaryOp)and isinstance(node.op,(UAdd,USub))and isinstance(node.operand,(Num,UnaryOp,BinOp)):
			operand=_convert(node.operand)
			if isinstance(node.op,UAdd):return+operand
			else:return-operand
		elif isinstance(node,BinOp)and isinstance(node.op,(Add,Sub))and isinstance(node.right,(Num,UnaryOp,BinOp))and isinstance(node.left,(Num,UnaryOp,BinOp)):
			left=_convert(node.left);right=_convert(node.right)
			if isinstance(node.op,Add):return left+right
			else:return left-right
		elif isinstance(node,Call):
			func_id=getattr(node.func,'id',_A)
			if func_id=='dict':return dict((k.arg,_convert(k.value))for k in node.keywords)
			elif func_id=='set':return set(_convert(node.args[0]))
			elif func_id=='date':return datetime.date(*[_convert(k)for k in node.args])
			elif func_id=='datetime':return datetime.datetime(*[_convert(k)for k in node.args])
		err=SyntaxError('malformed node or string: '+repr(node));err.filename='<string>';err.lineno=node.lineno;err.offset=node.col_offset;err.text=repr(node);err.node=node;raise err
	return _convert(node_or_string)
def _package_data(fn):
	data={}
	with open(fn,**open_kw)as fp:
		parsing=_C;lines=[]
		for line in fp.readlines():
			if sys.version_info<(3,):line=line.decode(_E)
			if line.startswith('_package_data'):
				if'dict('in line:parsing=_G;lines.append('dict(\n')
				elif line.endswith('= {\n'):parsing=_G;lines.append('{\n')
				else:raise NotImplementedError
				continue
			if not parsing:continue
			if parsing==_G:
				if line.startswith(')')or line.startswith('}'):
					lines.append(line)
					try:data=literal_eval(''.join(lines))
					except SyntaxError as e:
						context=2;from_line=e.lineno-(context+1);to_line=e.lineno+(context-1);w=len(str(to_line))
						for(index,line)in enumerate(lines):
							if from_line<=index<=to_line:
								print('{0:{1}}: {2}'.format(index,w,line).encode(_E),end='')
								if index==e.lineno-1:print('{0:{1}}  {2}^--- {3}'.format(' ',w,' '*e.offset,e.node))
						raise
					break
				lines.append(line)
			else:raise NotImplementedError
	return data
pkg_data=_package_data(__file__.replace(_F,_H))
exclude_files=[_F]
def _check_convert_version(tup):
	ret_val=str(tup[0]);next_sep=_B;nr_digits=0;post_dev=_C
	for x in tup[1:]:
		if isinstance(x,int):
			nr_digits+=1
			if nr_digits>2:raise ValueError('too many consecutive digits after '+ret_val)
			ret_val+=next_sep+str(x);next_sep=_B;continue
		first_letter=x[0].lower();next_sep=''
		if first_letter in'abcr':
			if post_dev:raise ValueError('release level specified after post/dev: '+x)
			nr_digits=0;ret_val+='rc'if first_letter=='r'else first_letter
		elif first_letter in'pd':nr_digits=1;post_dev=_D;ret_val+='.post'if first_letter=='p'else'.dev'
		else:raise ValueError('First letter of "'+x+'" not recognised')
	if nr_digits==1 and post_dev:ret_val+='0'
	return ret_val
version_info=pkg_data['version_info']
version_str=_check_convert_version(version_info)
class MyInstallLib(install_lib.install_lib):
	def install(self):
		fpp=pkg_data[_I].split(_B);full_exclude_files=[os.path.join(*fpp+[x])for x in exclude_files];alt_files=[];outfiles=install_lib.install_lib.install(self)
		for x in outfiles:
			for full_exclude_file in full_exclude_files:
				if full_exclude_file in x:os.remove(x);break
			else:alt_files.append(x)
		return alt_files
class MySdist(_sdist):
	def initialize_options(self):
		_sdist.initialize_options(self);dist_base=os.environ.get(_N);fpn=getattr(getattr(self,'nsp',self),_I,_A)
		if fpn and dist_base:print(_O.format(dist_base,fpn));self.dist_dir=os.path.join(dist_base,fpn)
try:
	from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
	class MyBdistWheel(_bdist_wheel):
		def initialize_options(self):
			_bdist_wheel.initialize_options(self);dist_base=os.environ.get(_N);fpn=getattr(getattr(self,'nsp',self),_I,_A)
			if fpn and dist_base:print(_O.format(dist_base,fpn));self.dist_dir=os.path.join(dist_base,fpn)
	_bdist_wheel_available=_D
except ImportError:_bdist_wheel_available=_C
class NameSpacePackager:
	def __init__(self,pkg_data):
		assert isinstance(pkg_data,dict);self._pkg_data=pkg_data;self.full_package_name=self.pn(self._pkg_data[_I]);self._split=_A;self.depth=self.full_package_name.count(_B);self.nested=self._pkg_data.get(_P,_C)
		if self.nested:NameSpaceInstaller.install_namespaces=lambda x:_A
		self.command=_A;self.python_version();self._pkg=[_A,_A]
		if sys.argv[0]==_F and sys.argv[1]==_J and'--single-version-externally-managed'not in sys.argv:
			if os.environ.get('READTHEDOCS',_A)=='True':os.system('pip install .');sys.exit(0)
			if not os.environ.get('RUAMEL_NO_PIP_INSTALL_CHECK',_C):print('error: you have to install with "pip install ."');sys.exit(1)
		if self._pkg_data.get(_Q):Distribution.is_pure=lambda*args:_D
		else:Distribution.is_pure=lambda*args:_C
		for x in sys.argv:
			if x[0]=='-'or x==_F:continue
			self.command=x;break
	def pn(self,s):
		if sys.version_info<(3,)and isinstance(s,unicode):return s.encode(_E)
		return s
	@property
	def split(self):
		skip=[]
		if self._split is _A:
			fpn=self.full_package_name.split(_B);self._split=[]
			while fpn:self._split.insert(0,_B.join(fpn));fpn=fpn[:-1]
			for d in sorted(os.listdir(_B)):
				if not os.path.isdir(d)or d==self._split[0]or d[0]in'._':continue
				x=os.path.join(d,_H)
				if os.path.exists(x):
					pd=_package_data(x)
					if pd.get(_P,_C):skip.append(d);continue
					self._split.append(self.full_package_name+_B+d)
			if sys.version_info<(3,):self._split=[y.encode(_E)if isinstance(y,unicode)else y for y in self._split]
		if skip:0
		return self._split
	@property
	def namespace_packages(self):return self.split[:self.depth]
	def namespace_directories(self,depth=_A):
		res=[]
		for(index,d)in enumerate(self.split[:depth]):
			if index>0:d=os.path.join(*d.split(_B))
			res.append(_B+d)
		return res
	@property
	def package_dir(self):
		d={self.full_package_name:_B}
		if _R in self._pkg_data:return d
		if len(self.split)>1:d[self.split[0]]=self.namespace_directories(1)[0]
		return d
	def create_dirs(self):
		directories=self.namespace_directories(self.depth)
		if not directories:return
		if not os.path.exists(directories[0]):
			for d in directories:
				os.mkdir(d)
				with open(os.path.join(d,_H),'w')as fp:fp.write('import pkg_resources\npkg_resources.declare_namespace(__name__)\n')
	def python_version(self):
		supported=self._pkg_data.get('supported')
		if supported is _A:return
		if len(supported)==1:minimum=supported[0]
		else:
			for x in supported:
				if x[0]==sys.version_info[0]:minimum=x;break
			else:return
		if sys.version_info<minimum:print('minimum python version(s): '+str(supported));sys.exit(1)
	def check(self):
		A='develop'
		try:from pip.exceptions import InstallationError
		except ImportError:return
		if self.command not in[_J,A]:return
		prefix=self.split[0];prefixes=set([prefix,prefix.replace('_','-')])
		for p in sys.path:
			if not p:continue
			if os.path.exists(os.path.join(p,_F)):continue
			if not os.path.isdir(p):continue
			if p.startswith('/tmp/'):continue
			for fn in os.listdir(p):
				for pre in prefixes:
					if fn.startswith(pre):break
				else:continue
				full_name=os.path.join(p,fn)
				if fn==prefix and os.path.isdir(full_name):
					if self.command==A:raise InstallationError('Cannot mix develop (pip install -e),\nwith non-develop installs for package name {0}'.format(fn))
				elif fn==prefix:raise InstallationError('non directory package {0} in {1}'.format(fn,p))
				for pre in[x+_B for x in prefixes]:
					if fn.startswith(pre):break
				else:continue
				if fn.endswith('-link')and self.command==_J:raise InstallationError('Cannot mix non-develop with develop\n(pip install -e) installs for package name {0}'.format(fn))
	def entry_points(self,script_name=_A,package_name=_A):
		A='console_scripts'
		def pckg_entry_point(name):return'{0}{1}:main'.format(name,'.__main__'if os.path.exists('__main__.py')else'')
		ep=self._pkg_data.get('entry_points',_D)
		if isinstance(ep,dict):return ep
		if ep is _A:return
		if ep not in[_D,1]:
			if'='in ep:return{A:[ep]}
			script_name=ep
		if package_name is _A:package_name=self.full_package_name
		if not script_name:script_name=package_name.split(_B)[-1]
		return{A:['{0} = {1}'.format(script_name,pckg_entry_point(package_name))]}
	@property
	def url(self):
		url=self._pkg_data.get('url')
		if url:return url
		sp=self.full_package_name
		for ch in'_.':sp=sp.replace(ch,'-')
		return'https://sourceforge.net/p/{0}/code/ci/default/tree'.format(sp)
	@property
	def author(self):return self._pkg_data['author']
	@property
	def author_email(self):return self._pkg_data['author_email']
	@property
	def license(self):
		lic=self._pkg_data.get('license')
		if lic is _A:return'MIT license'
		return lic
	def has_mit_lic(self):return'MIT'in self.license
	@property
	def description(self):return self._pkg_data['description']
	@property
	def status(self):
		status=self._pkg_data.get('status','β').lower()
		if status in['α','alpha']:return 3,'Alpha'
		elif status in['β','beta']:return 4,'Beta'
		elif'stable'in status.lower():return 5,'Production/Stable'
		raise NotImplementedError
	@property
	def classifiers(self):
		attr='_'+sys._getframe().f_code.co_name
		if not hasattr(self,attr):setattr(self,attr,self._setup_classifiers())
		return getattr(self,attr)
	def _setup_classifiers(self):return sorted(set(['Development Status :: {0} - {1}'.format(*self.status),'Intended Audience :: Developers','License :: '+('OSI Approved :: MIT'if self.has_mit_lic()else'Other/Proprietary')+' License','Operating System :: OS Independent','Programming Language :: Python']+[self.pn(x)for x in self._pkg_data.get('classifiers',[])]))
	@property
	def keywords(self):return self.pn(self._pkg_data.get('keywords',[]))
	@property
	def install_requires(self):return self._analyse_packages[0]
	@property
	def install_pre(self):return self._analyse_packages[1]
	@property
	def _analyse_packages(self):
		if self._pkg[0]is _A:self._pkg[0]=[];self._pkg[1]=[]
		ir=self._pkg_data.get('install_requires')
		if ir is _A:return self._pkg
		if isinstance(ir,list):self._pkg[0]=ir;return self._pkg
		packages=ir.get('any',[])
		if isinstance(packages,string_type):packages=packages.split()
		if self.nested:
			parent_pkg=self.full_package_name.rsplit(_B,1)[0]
			if parent_pkg not in packages:packages.append(parent_pkg)
		implementation=platform.python_implementation()
		if implementation=='CPython':pyver='py{0}{1}'.format(*sys.version_info)
		elif implementation=='PyPy':pyver='pypy'if sys.version_info<(3,)else'pypy3'
		elif implementation==_K:pyver='jython'
		packages.extend(ir.get(pyver,[]))
		for p in packages:
			if p[0]=='*':p=p[1:];self._pkg[1].append(p)
			self._pkg[0].append(p)
		return self._pkg
	@property
	def extras_require(self):ep=self._pkg_data.get('extras_require');return ep
	@property
	def package_data(self):
		df=self._pkg_data.get('data_files',[])
		if self.has_mit_lic():df.append(_L);exclude_files.append(_L)
		if self._pkg_data.get('binary_only',_C):exclude_files.append(_H)
		debug('testing<<<<<')
		if'Typing :: Typed'in self.classifiers:debug('appending');df.append('py.typed')
		pd=self._pkg_data.get('package_data',{})
		if df:pd[self.full_package_name]=df
		if sys.version_info<(3,):
			for k in pd:
				if isinstance(k,unicode):pd[str(k)]=pd.pop(k)
		return pd
	@property
	def packages(self):s=self.split;return s+self._pkg_data.get(_R,[])
	@property
	def python_requires(self):return self._pkg_data.get('python_requires',_A)
	@property
	def ext_modules(self):
		I='Exception:';H='link error';G='compile error:';F='Windows';E='lib';D='src';C='ext_modules';B='test';A='name'
		if hasattr(self,'_ext_modules'):return self._ext_modules
		if _S in sys.argv:return
		if platform.python_implementation()==_K:return
		try:
			plat=sys.argv.index('--plat-name')
			if'win'in sys.argv[plat+1]:return
		except ValueError:pass
		self._ext_modules=[];no_test_compile=_C
		if'--restructuredtext'in sys.argv:no_test_compile=_D
		elif'sdist'in sys.argv:no_test_compile=_D
		if no_test_compile:
			for target in self._pkg_data.get(C,[]):ext=Extension(self.pn(target[A]),sources=[self.pn(x)for x in target[D]],libraries=[self.pn(x)for x in target.get(E)]);self._ext_modules.append(ext)
			return self._ext_modules
		print('sys.argv',sys.argv);import tempfile,shutil;from textwrap import dedent;import distutils.sysconfig,distutils.ccompiler;from distutils.errors import CompileError,LinkError
		for target in self._pkg_data.get(C,[]):
			ext=Extension(self.pn(target[A]),sources=[self.pn(x)for x in target[D]],libraries=[self.pn(x)for x in target.get(E)])
			if B not in target:self._ext_modules.append(ext);continue
			if sys.version_info[:2]==(3,4)and platform.system()==F:
				if'FORCE_C_BUILD_TEST'not in os.environ:self._ext_modules.append(ext);continue
			c_code=dedent(target[B])
			try:
				tmp_dir=tempfile.mkdtemp(prefix='tmp_ruamel_');bin_file_name=B+self.pn(target[A]);print('test compiling',bin_file_name);file_name=os.path.join(tmp_dir,bin_file_name+'.c')
				with open(file_name,'w')as fp:fp.write(c_code)
				compiler=distutils.ccompiler.new_compiler();assert isinstance(compiler,distutils.ccompiler.CCompiler);distutils.sysconfig.customize_compiler(compiler);compiler.add_include_dir(os.getcwd())
				if sys.version_info<(3,):tmp_dir=tmp_dir.encode(_E)
				compile_out_dir=tmp_dir
				try:compiler.link_executable(compiler.compile([file_name],output_dir=compile_out_dir),bin_file_name,output_dir=tmp_dir,libraries=ext.libraries)
				except CompileError:debug(G,file_name);print(G,file_name);continue
				except LinkError:debug(H,file_name);print(H,file_name);continue
				self._ext_modules.append(ext)
			except Exception as e:
				debug(I,e);print(I,e)
				if sys.version_info[:2]==(3,4)and platform.system()==F:traceback.print_exc()
			finally:shutil.rmtree(tmp_dir)
		return self._ext_modules
	@property
	def test_suite(self):return self._pkg_data.get('test_suite')
	def wheel(self,kw,setup):
		if _T not in sys.argv:return _C
		file_name='setup.cfg'
		if os.path.exists(file_name):return _C
		with open(file_name,'w')as fp:
			if os.path.exists(_L):fp.write('[metadata]\nlicense-file = LICENSE\n')
			else:print('\n\n>>>>>> LICENSE file not found <<<<<\n\n')
			if self._pkg_data.get(_Q):fp.write('[bdist_wheel]\nuniversal = 1\n')
		try:setup(**kw)
		except Exception:raise
		finally:os.remove(file_name)
		return _D
def main():
	A='tarfmt';dump_kw='--dump-kw'
	if dump_kw in sys.argv:import wheel,distutils,setuptools;print('python:    ',sys.version);print('setuptools:',setuptools.__version__);print('distutils: ',distutils.__version__);print('wheel:     ',wheel.__version__)
	nsp=NameSpacePackager(pkg_data);nsp.check();nsp.create_dirs();MySdist.nsp=nsp
	if pkg_data.get(A):MySdist.tarfmt=pkg_data.get(A)
	cmdclass=dict(install_lib=MyInstallLib,sdist=MySdist)
	if _bdist_wheel_available:MyBdistWheel.nsp=nsp;cmdclass[_T]=MyBdistWheel
	kw=dict(name=nsp.full_package_name,namespace_packages=nsp.namespace_packages,version=version_str,packages=nsp.packages,python_requires=nsp.python_requires,url=nsp.url,author=nsp.author,author_email=nsp.author_email,cmdclass=cmdclass,package_dir=nsp.package_dir,entry_points=nsp.entry_points(),description=nsp.description,install_requires=nsp.install_requires,extras_require=nsp.extras_require,license=nsp.license,classifiers=nsp.classifiers,keywords=nsp.keywords,package_data=nsp.package_data,ext_modules=nsp.ext_modules,test_suite=nsp.test_suite)
	if _S not in sys.argv and('--verbose'in sys.argv or dump_kw in sys.argv):
		for k in sorted(kw):v=kw[k];print('  "{0}": "{1}",'.format(k,v))
	if dump_kw in sys.argv:sys.argv.remove(dump_kw)
	try:
		with open('README.rst')as fp:kw['long_description']=fp.read();kw['long_description_content_type']='text/x-rst'
	except Exception:pass
	if nsp.wheel(kw,setup):return
	for x in['-c','egg_info','--egg-base','pip-egg-info']:
		if x not in sys.argv:break
	else:
		for p in nsp.install_pre:
			import subprocess;setup_path=os.path.join(*p.split(_B)+[_F]);try_dir=os.path.dirname(sys.executable)
			while len(try_dir)>1:
				full_path_setup_py=os.path.join(try_dir,setup_path)
				if os.path.exists(full_path_setup_py):pip=sys.executable.replace(_G,'pip');cmd=[pip,_J,os.path.dirname(full_path_setup_py)];subprocess.check_output(cmd);break
				try_dir=os.path.dirname(try_dir)
	setup(**kw)
main()
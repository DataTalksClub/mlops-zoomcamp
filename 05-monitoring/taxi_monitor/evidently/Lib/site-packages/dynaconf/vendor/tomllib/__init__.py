__all__='loads','load','TOMLDecodeError','dump','dumps'
from._parser import TOMLDecodeError,load,loads
from._writer import dump,dumps
TOMLDecodeError.__module__=__name__
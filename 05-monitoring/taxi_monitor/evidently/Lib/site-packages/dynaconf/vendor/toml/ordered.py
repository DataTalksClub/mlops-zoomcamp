from collections import OrderedDict
from.import TomlEncoder
from.import TomlDecoder
class TomlOrderedDecoder(TomlDecoder):
	def __init__(A):super(A.__class__,A).__init__(_dict=OrderedDict)
class TomlOrderedEncoder(TomlEncoder):
	def __init__(A):super(A.__class__,A).__init__(_dict=OrderedDict)
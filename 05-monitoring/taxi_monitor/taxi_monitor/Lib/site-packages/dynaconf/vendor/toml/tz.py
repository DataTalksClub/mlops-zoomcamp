from datetime import tzinfo,timedelta
class TomlTz(tzinfo):
	def __init__(A,toml_offset):
		B=toml_offset
		if B=='Z':A._raw_offset='+00:00'
		else:A._raw_offset=B
		A._sign=-1 if A._raw_offset[0]=='-'else 1;A._hours=int(A._raw_offset[1:3]);A._minutes=int(A._raw_offset[4:6])
	def tzname(A,dt):return'UTC'+A._raw_offset
	def utcoffset(A,dt):return A._sign*timedelta(hours=A._hours,minutes=A._minutes)
	def dst(A,dt):return timedelta(0)
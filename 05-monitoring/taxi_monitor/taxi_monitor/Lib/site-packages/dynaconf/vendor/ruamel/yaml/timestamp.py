from __future__ import print_function,absolute_import,division,unicode_literals
import datetime,copy
if False:from typing import Any,Dict,Optional,List
class TimeStamp(datetime.datetime):
	def __init__(A,*B,**C):A._yaml=dict(t=False,tz=None,delta=0)
	def __new__(A,*B,**C):return datetime.datetime.__new__(A,*B,**C)
	def __deepcopy__(A,memo):B=TimeStamp(A.year,A.month,A.day,A.hour,A.minute,A.second);B._yaml=copy.deepcopy(A._yaml);return B
import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import batch
import pandas as pd

def put_file_s3local(year, month):
    actual_output = batch.main(year,month)
    
    expected_output = '2023-01.parquet'
    
    assert expected_output == actual_output

if __name__ == '__main__':
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    put_file_s3local(year,month)
   

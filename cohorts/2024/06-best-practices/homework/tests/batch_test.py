from datetime import datetime
import pandas as pd
from deepdiff import DeepDiff
import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
 
# # directory reach
# directory = Path(__file__).parent
# print(directory.parent) 
# # setting path
# sys.path.append(directory.parent) 
import batch

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

def test_dataframe():
    data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
    ]

    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    exp_df = pd.DataFrame(data, columns=columns)
    
    print(exp_df)
    # exp_df_dict = exp_df.to_dict('dict')
    # actual_df = batch.main(2023,1)
    # actual_df_dict = actual_df.to_dict('dict')

    # diff = DeepDiff(actual_df_dict, exp_df_dict, significant_digits=1)
    # print(f'diff={diff}')

    # # # this will check if there is a content mismatch between the expected and actual response
    # assert 'type_changes' not in diff
    # assert 'value_changes' not in diff
    
if __name__=='__main__':
    test_dataframe()

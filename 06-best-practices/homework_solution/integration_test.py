import os

from datetime import datetime
import pandas as pd

import batch

def dt(hour, minute, second=0):
    return datetime(2021, 1, 1, hour, minute, second)


S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')

options = {
    'client_kwargs': {
        'endpoint_url': S3_ENDPOINT_URL
    }
}

data = [
    (None, None, dt(1, 2), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
    (1, 1, dt(1, 2, 0), dt(2, 2, 1)),        
]

columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
df_input = pd.DataFrame(data, columns=columns)


input_file = batch.get_input_path(2021, 1)
output_file = batch.get_output_path(2021, 1)

df_input.to_parquet(
    input_file,
    engine='pyarrow',
    compression=None,
    index=False,
    storage_options=options
)


os.system('python batch.py 2021 1')


df_actual = pd.read_parquet(output_file, storage_options=options)


assert abs(df_actual['predicted_duration'].sum() - 69.28) < 0.1
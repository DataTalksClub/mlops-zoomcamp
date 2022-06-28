#!/usr/bin/env python
# coding: utf-8


#get_ipython().system('pip freeze | grep scikit-learn')

import pickle
import pandas as pd
import numpy as np
import os
import sys


with open('model.bin', 'rb') as f_in:
    dv, lr = pickle.load(f_in)

categorical = ['PUlocationID', 'DOlocationID']

def read_data(filename):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df


def run(year, month):
    df = read_data(f'https://nyc-tlc.s3.amazonaws.com/trip+data/fhv_tripdata_{year:04d}-{month:02d}.parquet')

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)
    print(f'mean of prediction is is {np.mean(y_pred)}')

    df['ride_id'] = f'{year:04d}/{month:02d}_'+df.index.astype('str')
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predictions'] = y_pred

    output_file = f'{year:04d}-{month:02d}_'+'results.parquet'
    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )

    print(f'output file size is {os.path.getsize(output_file)/(1024**2)} MB')


if __name__ == '__main__':
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    run(year, month)




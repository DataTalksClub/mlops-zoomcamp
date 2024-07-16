#!/usr/bin/env python
# coding: utf-8
import os
import sys
import pickle
import pandas as pd
import subprocess

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL","https://mlflow-artifacts-gansi.s3.eu-north-1.amazonaws.com/")
options = {
        'client_kwargs': {
            'endpoint_url': S3_ENDPOINT_URL 
            }
        }
def read_data(filename) :
    
    df = pd.read_parquet(filename,storage_options=options)

    return df


def prepare_data(df, categorical):
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df



def get_input_path(year, month):
    default_input_pattern = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    ip_file = default_input_pattern.format(year=year, month=month)
    print(ip_file)

    if os.getenv('INPUT_FILE_PATTERN'):
        local_s3_file = os.getenv('INPUT_FILE_PATTERN').format(year=year, month=month)
        cmd='curl {ip_file} | aws --endpoint-url {S3_ENDPOINT_URL} s3 cp - {local_s3_file}'.format(ip_file=ip_file,S3_ENDPOINT_URL=S3_ENDPOINT_URL,local_s3_file=local_s3_file) 
    else:
        local_s3_file = "s3://mlflow-artifacts-gansi/in/taxi_type=yellow/{year:04d}-{month:02d}.parquet".format(year=year,month=month)
        cmd="curl {ip_file} | aws s3 cp - {local_s3_file}".format(ip_file=ip_file,local_s3_file=local_s3_file)
    print(cmd)
    push=subprocess.run(cmd, shell=True, stdout = subprocess.PIPE)
    print(push.returncode)
    return local_s3_file

def get_output_path(year, month):
    default_output_pattern = "s3://mlflow-artifacts-gansi/in/taxi_type=yellow/{year:04d}-{month:02d}.parquet"
    op_file = default_output_pattern.format(year=year, month=month)
    print(op_file)

    if os.getenv('OUTPUT_FILE_PATTERN'):
        local_s3_file = os.getenv('OUTPUT_FILE_PATTERN').format(year=year, month=month)
    else:
        local_s3_file = "s3://mlflow-artifacts-gansi/out/taxi_type=yellow/{year:04d}-{month:02d}.parquet"
    return local_s3_file

# def get_output_path(year, month):
#     default_output_pattern = 's3://nyc-duration/taxi_type=fhv/year={year:04d}/month={month:02d}.parquet'
#     output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
#     return output_pattern.format(year=year, month=month)


def main(year, month):
    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)
    
    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    categorical = ['PULocationID', 'DOLocationID']

    df = read_data(input_file)
    df = prepare_data(df, categorical)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')


    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)


    print('predicted mean duration:', y_pred.mean())


    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=options
    )

    # cmd = "aws --endpoint-url {S3_ENDPOINT_URL} s3 ls"
    # get=subprocess.run(cmd, check=True, shell=True, stdout = subprocess.PIPE).stdout
    # print(get)
    get_op_file = output_file[output_file.rfind("/")+1:]
    print(get_op_file,output_file)
    return get_op_file



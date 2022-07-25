import os
import subprocess
import sys
from datetime import datetime

import boto3
import pandas as pd

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://localhost:4566")
INPUT_FILE_PATTERN = os.getenv("INPUT_FILE_PATTERN", None)
OUTPUT_FILE_PATTERN = os.getenv("OUTPUT_FILE_PATTERN", None)
BUCKET_NAME = os.getenv("BUCKET_NAME", "nyc-duration")


def dt(hour, minute, second=0):
    """Function to prepare datetime object"""

    return datetime(2021, 1, 1, hour, minute, second)


def test_data_prep(year: int = None, month: int = None):
    """Test function to create fake data in bucket and checks if data exists"""

    data = [
        (None, None, dt(1, 2), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
        (1, 1, dt(1, 2, 0), dt(2, 2, 1)),
    ]

    columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
    df_input = pd.DataFrame(data, columns=columns)

    options = {'client_kwargs': {'endpoint_url': S3_ENDPOINT_URL}}

    input_file = INPUT_FILE_PATTERN.format(year=year, month=month)

    df_input.to_parquet(
        input_file, engine='pyarrow', compression=None, index=False, storage_options=options
    )

    client = boto3.client('s3', endpoint_url=S3_ENDPOINT_URL)

    # Check if file as been created as intended in the bucket
    response = client.head_object(
        Bucket=BUCKET_NAME, Key='in/{year:04d}-{month:02d}.parquet'.format(year=year, month=month)
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_save_data(year, month):
    """Test function to make sure file is processed and saved in S3"""

    subprocess.run(['python ../batch.py %s %s' % (year, month)], shell=True)
    client = boto3.client('s3', endpoint_url=S3_ENDPOINT_URL)

    # Check if file as been created as intended in the bucket
    year = int(year)
    month = int(month)
    response = client.head_object(
        Bucket=BUCKET_NAME, Key='out/{year:04d}-{month:02d}.parquet'.format(year=year, month=month)
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_output_predictions(year, month):
    """Test predictions of the output file"""

    options = {'client_kwargs': {'endpoint_url': S3_ENDPOINT_URL}}

    output_file = OUTPUT_FILE_PATTERN.format(year=year, month=month)

    df = pd.read_parquet(output_file, storage_options=options)
    output_result = df["predicted_duration"].sum()
    expected_result = 69.28869683240714

    assert output_result == expected_result


if __name__ == "__main__":

    year = sys.argv[1]
    month = sys.argv[2]
    test_data_prep(year=int(year), month=int(month))
    test_save_data(year=year, month=month)
    test_output_predictions(year=int(year), month=int(month))

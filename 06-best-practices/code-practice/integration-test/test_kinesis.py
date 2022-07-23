import json
import time

import boto3
import deepdiff
import requests

url = "http://localhost:8080/2015-03-31/functions/function/invocations"

event = {
    "Records": [
        {
            "kinesis": {
                "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ==",
            },
        }
    ]
}

client = boto3.client('kinesis', endpoint_url="http://localhost:4566")

response = requests.post(url=url, json=event).json()

shard_id = "shardId-000000000000"
stream_name = "prediction-service"
if response["statusCode"] == 200:

    time.sleep(5)
    shard_iterator_response = client.get_shard_iterator(StreamName=stream_name,
                                                        ShardId=shard_id,
                                                        ShardIteratorType='TRIM_HORIZON'
                                                        )
    
    shard_iterator_id = shard_iterator_response['ShardIterator']


    records_response = client.get_records(
        ShardIterator=shard_iterator_id,
        Limit=1,
    )

    records = records_response["Records"]

    assert len(records) == 1

    actual_record = json.loads(records[0]['Data'])
    expected_record = {'model': 'ride_prediction_model',
                         'version': '20c7e3f3b3584b769bf6cacd4643d43d',
                         'prediction': {'ride_id': 256,
                                        'prediction': 18.019
                                        }
                        }

    diff =  deepdiff.DeepDiff(actual_record, expected_record, significant_digits=2)

    assert "type_changes" not in diff
    assert "values_changed" not in diff

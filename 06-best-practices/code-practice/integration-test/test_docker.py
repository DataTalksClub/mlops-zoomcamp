import requests
import deepdiff

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

actual_response = requests.post(url=url, json=event).json()
expected_response = {'statusCode': 200,
                     'predictions': [
                        {'model': 'ride_prediction_model',
                         'version': '20c7e3f3b3584b769bf6cacd4643d43d',
                         'prediction': {'ride_id': 256,
                                        'prediction': 18.019
                                        }
                        }]
                    }

diff = deepdiff.DeepDiff(actual_response, expected_response, significant_digits=2)

assert "type_changes" not in diff
assert "values_changed" not in diff

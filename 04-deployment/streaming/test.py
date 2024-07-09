
import lambda_function

event = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49653474394924980099995190332180326141369034480937861122",
                "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDE1NgogICAgfQ==",
                "approximateArrivalTimestamp": 1719794254.73
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49653474394924980099995190332180326141369034480937861122",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::068644365850:role/lambda-kinesis-role",
            "awsRegion": "eu-north-1",
            "eventSourceARN": "arn:aws:kinesis:eu-north-1:068644365850:stream/ride_events"
        }
    ]
}

result = lambda_function.lambda_handler(event, None)
print(result)

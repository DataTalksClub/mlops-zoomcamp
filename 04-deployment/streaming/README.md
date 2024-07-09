## Machine Learning for Streaming

* Scenario
* Creating the role 
* Create a Lambda function, test it
* Create a Kinesis stream
* Connect the function to the stream
* Send the records 

Links

* [Tutorial: Using Amazon Lambda with Amazon Kinesis](https://docs.amazonaws.cn/en_us/lambda/latest/dg/with-kinesis-example.html)

## Code snippets

### Sending data


```bash
KINESIS_STREAM_INPUT=ride_events
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --data "Hello, this is a test."
```

Decoding base64

```python
base64.b64decode(data_encoded).decode('utf-8')
```

Record example

```json
{
    "ride": {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66
    }, 
    "ride_id": 156
}
```

Sending this record

```bash
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --data '{
        "ride": {
            "PULocationID": 256,
            "DOLocationID": 256,
            "trip_distance": 256
        }, 
        "ride_id": 256
    }'
```

### Test event


```json
{
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49630081666084879290581185630324770398608704880802529282",
                "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ==",
                "approximateArrivalTimestamp": 1654161514.132
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49630081666084879290581185630324770398608704880802529282",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::XXXXXXXXX:role/lambda-kinesis-role",
            "awsRegion": "eu-west-1",
            "eventSourceARN": "arn:aws:kinesis:eu-west-1:XXXXXXXXX:stream/ride_events"
        }
    ]
}
```

### Reading from the stream

```bash
KINESIS_STREAM_OUTPUT='ride_predictions'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT} | jq -r '.Records[0].Data' | base64 -di --decode | jq
``` 


### Running the test

```bash
export PREDICTIONS_STREAM_NAME="ride_predictions"
export RUN_ID="9129b1c2b1ce401e9ab1d1d94a19249b"
export TEST_RUN="True"

python test.py
```

### Putting everything to Docker

```bash
docker build -t streaming-model-duration:v1 .

docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="e1efc53e9bd149078b0c12aeaa6365df" \
    -e TEST_RUN="True" \
    -e AWS_DEFAULT_REGION="eu-west-1" \
    stream-model-duration:v1
```

URL for testing:

* http://localhost:8080/2015-03-31/functions/function/invocations



### Configuring AWS CLI to run in Docker

To use AWS CLI, you may need to set the env variables:

https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-envvars.html


```bash

export AWS_DEFAULT_REGION="eu-north-1"
export AWS_ACCESS_KEY_ID=AKIAQ764F4YNBHPE2AUS
export AWS_SECRET_ACCESS_KEY=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

docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="e1efc53e9bd149078b0c12aeaa6365df" \
    -e TEST_RUN="True" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
    stream-model-duration:v1
```

Alternatively, you can mount the `.aws` folder with your credentials to the `.aws` folder in the container:

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="9129b1c2b1ce401e9ab1d1d94a19249b" \
    -e TEST_RUN="True" \
    -v c:/Users/arunganesan/.aws:/root/.aws \
    streaming-model-duration:v1
```

### Publishing Docker images

Creating an ECR repo - Elastic container registry for hosting docker images

```bash
aws ecr create-repository --repository-name duration-pred-model
```
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:eu-north-1:068644365850:repository/duration-model",
        "registryId": "068644365850",
        "repositoryName": "duration-model",
        "repositoryUri": "068644365850.dkr.ecr.eu-north-1.amazonaws.com/duration-model",
        "createdAt": 1720139341.551,
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": false
        },
        "encryptionConfiguration": {
            "encryptionType": "AES256"
        }
    }
}

Logging in

```bash
$(aws ecr get-login --no-include-email)
```

Pushing 

```bash
REMOTE_URI="068644365850.dkr.ecr.eu-north-1.amazonaws.com/duration-pred-model2"
REMOTE_TAG="v1"
REMOTE_IMAGE=${REMOTE_URI}:${REMOTE_TAG}

LOCAL_IMAGE="streaming-model-duration:v1"
docker tag ${LOCAL_IMAGE} ${REMOTE_IMAGE}
docker push ${REMOTE_IMAGE}
```


ip = base64.b64encode(b'{
    "ride": {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66
    }, 
    "ride_id": 156
}')

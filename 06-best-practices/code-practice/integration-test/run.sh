#!/bin/bash
cd "$(dirname "$0")"


if [ "${LOCAL_IMAGE_NAME}" == "" ]; then 
    LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
    export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"
    echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_IMAGE_NAME}"
    docker build -t ${LOCAL_IMAGE_NAME} ..
else
    echo "no need to build image ${LOCAL_IMAGE_NAME}"
fi



export STREAM_NAME="prediction-service"
export RUN_ID="20c7e3f3b3584b769bf6cacd4643d43d"
export TEST_RUN=False
export AWS_ACCESS_KEY_ID=$(aws configure get lamda_kinesis.aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get lamda_kinesis.aws_secret_access_key)
export AWS_DEFAULT_REGION=$(aws configure get lamda_kinesis.region)
export KINESIS_ENDPOINT_URL='http://localstack:4566/'

docker-compose config

docker-compose up -d

sleep 5

aws --endpoint-url http://localhost:4566  kinesis create-stream --stream-name $STREAM_NAME --shard-count 1 

sleep 5

pipenv run python test_docker.py
RESULT=$?

if [ $RESULT -eq 0 ]; then
  echo model lambda integration tests passed
else
  docker-compose logs
  echo model lambda integration tests failed
fi


pipenv run python test_kinesis.py
RESULT=$?
if [ $RESULT -eq 0 ]; then
  echo kinesis integration test passed
else
  docker-compose logs
  echo kinesis integration tests failed
fi
docker-compose down

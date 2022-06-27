#!/bin/bash
export STREAM_NAME="ride_predictions"
export RUN_ID="20c7e3f3b3584b769bf6cacd4643d43d"
export TEST_RUN=$1
export AWS_ACCESS_KEY_ID=$(aws configure get lamda_kinesis.aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get lamda_kinesis.aws_secret_access_key)
export AWS_DEFAULT_REGION=$(aws configure get lamda_kinesis.region)

docker run -it --rm \
    -p 8080:8080 \
    -e STREAM_NAME=$STREAM_NAME \
    -e RUN_ID=$RUN_ID \
    -e TEST_RUN=$TEST_RUN \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} \
    streaming-week4:latest  

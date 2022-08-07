#!/bin/bash

cd "$(dirname "$0")"

# Some variables

ENV=$1
export RUN_ID="20c7e3f3b3584b769bf6cacd4643d43d"
export TEST_RUN=False
export MODEL_BUCKET_DEV="mlops-zoomcamp-nakul"

if [[ $ENV == "stage" ]]
    then 
    export STREAM_NAME="ride_predictions_${ENV}"
    export MODEL_BUCKET="mlops-zoomcamp-nakul-${ENV}"
else
    export STREAM_NAME="ride_predictions"
    export MODEL_BUCKET="mlops-zoomcamp-nakul"
fi 

# run terraform for ${ENV}
terraform init 
TF_VAR_run_id=$RUN_ID TF_VAR_test_run=$TEST_RUN terraform apply -auto-approve -var-file="vars/${ENV}.tfvars"

# copy model artifacts
aws s3 sync s3://${MODEL_BUCKET_DEV} s3://${MODEL_BUCKET}

# update the environment variables for lambda function
variables="{STREAM_NAME=${STREAM_NAME}, MODEL_BUCKET=${MODEL_BUCKET}, RUN_ID=${RUN_ID}, TEST_RUN=${TEST_RUN}}"
aws --region us-east-2 lambda update-function-configuration --function-name ride-prediction-service-${ENV} --environment "Variables=${variables}"

#!/bin/bash

export AWS_ACCOUNT_ID="135015496169"
export AWS_DEFAULT_REGION=$(aws configure get lamda_kinesis.region)

aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
docker tag bc643c58edb8 $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/ride-predictions-streaming:latest

docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/ride-predictions-streaming:latest

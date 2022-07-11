#!/bin/bash

export AWS_ACCESS_KEY_ID=$(aws configure get lamda_kinesis.aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get lamda_kinesis.aws_secret_access_key)
export AWS_DEFAULT_REGION=$(aws configure get lamda_kinesis.region)
docker compose -f docker-compose-practice.yml up --build --force-recreate

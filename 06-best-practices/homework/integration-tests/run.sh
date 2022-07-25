#!/bin/bash
cd "$(dirname "$0")"
export BUCKET_NAME="nyc-duration"
export INPUT_FILE_PATTERN="s3://${BUCKET_NAME}/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://${BUCKET_NAME}/out/{year:04d}-{month:02d}.parquet"
export S3_ENDPOINT_URL="http://localhost:4566/"

# creating bucket in localstack
docker-compose up -d 

aws --endpoint-url ${S3_ENDPOINT_URL} s3 mb s3://${BUCKET_NAME}

# run integration tests
python test_batch.py 2021 01

RESULT=$?

if [ $RESULT -eq 0 ]; then
  echo Integration tests passed
else
  docker-compose logs
  echo Integration tests failed
fi

docker-compose down

## remove an s3 bucket
```bash
aws s3 rm s3://nyc-duration --recursive
```
## create a localstack s3 bucket
aws s3 mb s3://nyc-duration --endpoint-url http://localhost:4566

## list all buckets locally
aws s3 ls --endpoint-url http://localhost:4566

```bash
export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
export S3_ENDPOINT_URL="http://localhost:4566"
```

```bash
export AWS_DEFAULT_REGION="eu-north-1"
export AWS_ACCESS_KEY_ID=AKIAQ764F4YNBHPE2AUS
export AWS_SECRET_ACCESS_KEY=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
```

```bash
curl "https://download-link-address/" | aws s3 cp - s3://aws-bucket/data-file
```

# get details of the files in the bucket

```bash
 aws s3 ls --endpoint-url http://localhost:4566 s3://nyc-duration/out/ --human-readable --summarize
 ```

 
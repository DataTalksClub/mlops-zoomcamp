terraform {
  required_version = ">= 0.12"
}

provider "aws" {
  region = var.aws_region
}

module "source_kinesis_stream" {
    source           = "./modules/kinesis"
    stream_name      = "source_kinesis_stream"
    retention_period = 48
    shard_count      = 2
    tags           = "terraform-kinesis-lambda"
}

module "output_kinesis_stream" {
    source           = "./modules/kinesis"
    stream_name      = "output_kinesis_stream"
    retention_period = 48
    shard_count      = 2
    tags           = "terraform-kinesis-lambda"
}

module "s3_bucket" {
  source = "./modules/s3"
  bucket_name = "mlflow-models-test"
}

module "lambda_function" {
  source              = "./modules/lambda"
  lambda_function_name = "test-lambda"  # TODO: change to prediction lambda
  source_stream_name = module.source_kinesis_stream.stream_name
  source_stream_arn = module.source_kinesis_stream.stream_arn
  output_stream_name = module.output_kinesis_stream.stream_name
  output_stream_arn = module.output_kinesis_stream.stream_arn
  bucket_name = module.s3_bucket.name
}
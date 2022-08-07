terraform {
    backend "s3" {
        bucket  = "tf-state-mlops-zoomcamp-nbajaj"
        key     = "mlops-zoomcamp-stage.tfstate"
        region  = "us-east-1"
        encrypt = true
    }
    required_version = ">= 1.0"
}

provider "aws" {
    profile = "mlopszoomcamp_infra"
    region = var.aws_region
}

data "aws_caller_identity" "current" {}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

locals {
  account_id = data.aws_caller_identity.current.account_id
}

module "lambda_ecr_image" {
    source = "./modules/ecr"
    repo_name = var.env == "prod" ? "${var.lambda_ride_prediction_repo}" : "${var.lambda_ride_prediction_repo}-${var.env}"
    account_id = local.account_id
    lambda_function_local_path = var.lambda_function_local_path
    docker_image_local_path = var.docker_image_local_path
    ecr_image_tag = var.lambda_ride_prediction_tag
    run_id = var.run_id 
    model_bucket = var.env == "prod" ? var.ride_prediction_bucket_name : "${var.ride_prediction_bucket_name}-${var.env}"
    test_run = var.test_run
    stream_name = var.env == "prod" ? "${var.output_stream_name}" : "${var.output_stream_name}_${var.env}"
}

module "kinesis_source_stream" {
    source = "./modules/kinesis"
    stream_name = var.env == "prod" ? "${var.source_stream_name}" : "${var.source_stream_name}_${var.env}"
    shard_count = 2
    retention_period = 48
    tags = var.env
}

module "kinesis_output_stream" {
    source = "./modules/kinesis"
    stream_name = var.env == "prod" ? "${var.output_stream_name}" : "${var.output_stream_name}_${var.env}"
    shard_count = 2
    retention_period = 48
    tags = var.env
}

module "model_bucket" {
    source = "./modules/storage"
    bucket = var.env == "prod" ? var.ride_prediction_bucket_name : "${var.ride_prediction_bucket_name}-${var.env}"
    tags = var.env
}

module "ride_prediction_lambda" {
    source = "./modules/lambda"
    output_kinesis_stream_arn = module.kinesis_output_stream.stream_arn
    input_kinesis_stream_arn = module.kinesis_source_stream.stream_arn
    iam_role_name_lambda = var.env == "prod" ? "lambda-kinesis": "lambda-kinesis-${var.env}"
    function_name = var.env == "prod" ? "ride-prediction-service": "ride-prediction-service-${var.env}"
    stream_name = var.env == "prod" ? "${var.output_stream_name}" : "${var.output_stream_name}_${var.env}"
    image_uri = module.lambda_ecr_image.image_uri
    model_bucket = var.env == "prod" ? var.ride_prediction_bucket_name : "${var.ride_prediction_bucket_name}-${var.env}"
    model_bucket_arn = module.model_bucket.bucket_arn
}

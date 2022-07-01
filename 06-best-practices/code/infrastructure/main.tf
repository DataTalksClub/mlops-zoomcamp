# Make sure to create state bucket beforehand
terraform {
  required_version = ">= 1.0"
  backend "s3" {
    bucket  = "tf-state-mlops-zoomcamp"
    key     = "mlops-zoomcamp.tfstate"
    region  = "eu-west-1"
    encrypt = true
  }
}

terraform {
  required_version = ">= 0.12"
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current_identity" {}

locals {
  account_id                  = data.aws_caller_identity.current_identity.account_id
  project_id                  = "mlops-zoomcamp"  # var.project_id
  region                      = var.aws_region

  lambda_function_local_path  = "../lambda_function.py"
  docker_image_local_path     = "../Dockerfile"
  ecr_repo_name               = "stream_model_duration_${local.project_id}"
  lambda_function_name        = "prediction_lambda_${local.project_id}"
  model_bucket                = "mlflow-models-${local.project_id}"
  source_stream_name          = "ride_events_${local.project_id}"
  output_kinesis_stream       = "ride_predictions_${local.project_id}"
}

module "ecr_image" {
  source = "./modules/ecr"
  ecr_repo_name = local.ecr_repo_name
   account_id = local.account_id
   lambda_function_local_path = local.lambda_function_local_path
   docker_image_local_path = local.docker_image_local_path
}

module "source_kinesis_stream" {
    source           = "./modules/kinesis"
    stream_name      = local.source_stream_name
    retention_period = 48
    shard_count      = 2
    tags             = local.project_id
}

module "output_kinesis_stream" {
    source           = "./modules/kinesis"
    stream_name      = local.output_kinesis_stream
    retention_period = 48
    shard_count      = 2
    tags           = local.project_id
}

module "s3_bucket" {
  source = "./modules/s3"
  bucket_name = local.model_bucket
}

module "lambda_function" {
  source                  = "./modules/lambda"
  lambda_function_name    = local.lambda_function_name
  image_uri               = module.ecr_image.image_uri
  source_stream_name      = local.source_stream_name
  source_stream_arn       = module.source_kinesis_stream.stream_arn
  output_stream_name      = local.output_kinesis_stream
  output_stream_arn       = module.output_kinesis_stream.stream_arn
  model_bucket            = module.s3_bucket.name
}

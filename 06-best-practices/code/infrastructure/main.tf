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
  account_id            = data.aws_caller_identity.current_identity.account_id
  prefix                = "mlops-zoomcamp"
  region                = "eu-west-1"
  lambda_function_local_path  = "../lambda_function.py"
  docker_image_local_path = "../Dockerfile"
  source_stream_name = "${local.prefix}_source_kinesis_stream"
  output_kinesis_stream = "${local.prefix}_output_kinesis_stream"

}

module "ecr_image" {
  source = "./modules/ecr"
  ecr_repo_name = "${local.prefix}-image-repo"
  account_id = local.account_id
  lambda_function_local_path = local.lambda_function_local_path
  docker_image_local_path = local.docker_image_local_path
}

module "source_kinesis_stream" {
    source           = "./modules/kinesis"
    stream_name      = local.source_stream_name
    retention_period = 48
    shard_count      = 2
    tags           = local.prefix
}

module "output_kinesis_stream" {
    source           = "./modules/kinesis"
    stream_name      = local.output_kinesis_stream
    retention_period = 48
    shard_count      = 2
    tags           = local.prefix
}

module "s3_bucket" {
  source = "./modules/s3"
  bucket_name = "${local.prefix}-mlflow-models"
}

module "lambda_function" {
  source              = "./modules/lambda"
  lambda_function_name = "${local.prefix}-prediction-lambda"
  image_uri = module.ecr_image.image_uri
  source_stream_name = local.source_stream_name
  source_stream_arn = module.source_kinesis_stream.stream_arn
  output_stream_name = local.output_kinesis_stream
  output_stream_arn = module.output_kinesis_stream.stream_arn
  bucket_name = module.s3_bucket.name
}
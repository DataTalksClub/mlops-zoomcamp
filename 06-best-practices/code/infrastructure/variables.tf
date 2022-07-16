variable "aws_region" {
  description = "AWS region to create resources"
  default     = "eu-west-1"
}

variable "project_id" {
  description = "project_id"
  default = "mlops-zoomcamp"
}

variable "source_stream_name" {
  description = ""
}

variable "output_stream_name" {
  description = ""
}

variable "model_bucket" {
  description = "s3_bucket"
}

variable "lambda_function_local_path" {
  description = ""
}

variable "docker_image_local_path" {
  description = ""
}

variable "ecr_repo_name" {
  description = ""
}

variable "lambda_function_name" {
  description = ""
}
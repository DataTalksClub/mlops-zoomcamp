variable "aws_region" {
  description = "AWS region to create resources"
  default     = "us-east-2"
}

variable "lambda_ride_prediction_repo" {
  description = "ecr repo name for ride prediction"
  default = "ride-predictions-streaming"
}

variable "env" {
  description = "Environment name passed"
  default = "stage"
}

variable "source_stream_name" {
  default = "ride_events"
  
}

variable "output_stream_name" {
  default = "ride_predictions"
}

variable "lambda_function_local_path" {
  description = "path to local lambda function"
  default = "../lambda_function.py"
}

variable "docker_image_local_path" {
  description = "path to local docker image for lambda"
  default = "../Dockerfile"
}

variable "lambda_ride_prediction_tag" {
  description = "tag name for the ecr image of lambda function"
  default = "latest"
}

variable "ride_prediction_bucket_name" {
  description = "name of the bucket where model is deployed"
  default = "mlops-zoomcamp-nakul"
}

variable "run_id" {
    type = string
    description = "model version"
}

variable "test_run"{
    type = string
    description = "type of run whether test or not"
    default = "False"
}

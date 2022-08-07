variable "repo_name" {
    description = "Name of the repo in ECR"
    default = "taxi_rides"
}

variable "ecr_image_tag" {
    description = "Tag for the image"
    default = "latest"
}

variable "lambda_function_local_path" {
    description = "path to lambda file"
}

variable "docker_image_local_path" {
    description = "path to docker file"
}

variable "region" {
    description = "region for the repo"
    default = "us-east-1"
}

variable "account_id" {
}

variable "stream_name" {
    type = string
    description = "output stream name"
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

variable "model_bucket" {
    type = string
    description = "name of bucket where model artifacts are stored"
}
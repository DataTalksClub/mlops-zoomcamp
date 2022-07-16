variable "source_stream_name" {
  type        = string
  description = "Source Kinesis Data Streams stream name"
}

variable "source_stream_arn" {
  type        = string
  description = "Source Kinesis Data Streams stream name"
}

variable "output_stream_name" {
  description = "Name of output stream where all the events will be passed"
}

variable "output_stream_arn" {
  description = "ARN of output stream where all the events will be passed"
}

variable "model_bucket" {
  description = "Name of the bucket"
}

variable "lambda_function_name" {
  description = "Name of the lambda function"
}

variable "image_uri" {
  description = "ECR image uri"
}

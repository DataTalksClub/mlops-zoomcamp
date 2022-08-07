variable "output_kinesis_stream_arn" {
    description = "Arn for the output stream"
}

variable "input_kinesis_stream_arn" {
    description = "Arn for the input kinesis stream"
}

variable "iam_role_name_lambda" {
    description = "Role name for iam role"
}

variable "function_name" {
    description = "Lambda function name"
}

variable "stream_name" {
    description = "Name of the project or service associated with the lambda"
}

variable "image_uri" {
    description = "url destination of the image whether in aws ecr or docker hub"
}

variable "model_bucket" {
    description = "bucket name for where ml model is stored" 
}

variable "model_bucket_arn" {
    description = "s3 bucket arn reference"
}
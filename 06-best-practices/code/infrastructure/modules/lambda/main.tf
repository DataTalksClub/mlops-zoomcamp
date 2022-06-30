resource "aws_lambda_function" "kinesis_lambda" {
  // filename      = "lambda_function.zip" # var
  // source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name = var.lambda_function_name
  image_uri = var.image_uri
  package_type = "Image"
  role          = aws_iam_role.lambda_for_kinesis.arn   # to be updated
//  handler       = "lambda_function.lambda_handler"
//  runtime = "python3.8"
  tracing_config {
    mode = "Active"
  }
  environment {
    variables = {
      OUTPUT_KINESIS_STREAM = var.output_stream_name
      BUCKET_NAME = var.bucket_name
    }
  }
  timeout = 180
}

# Lambda Invoke & Event Source Mapping:

resource "aws_lambda_function_event_invoke_config" "kinesis_lambda_event" {
  function_name                = var.lambda_function_name # "lambda_function"
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}

resource "aws_lambda_event_source_mapping" "kinesis_mapping" {
  event_source_arn  = var.source_stream_arn
  function_name     = aws_lambda_function.kinesis_lambda.arn
  starting_position = "LATEST"
  depends_on = [
    aws_iam_role_policy_attachment.kinesis_processing
  ]
  // enabled           = var.lambda_event_source_mapping_enabled
  // batch_size        = var.lambda_event_source_mapping_batch_size
}

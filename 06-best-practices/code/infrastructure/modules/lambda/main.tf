resource "aws_lambda_function" "kinesis_lambda" {
  function_name = var.lambda_function_name
  image_uri = var.image_uri
  package_type = "Image"
  role          = aws_iam_role.lambda_for_kinesis.arn   # to be updated
  tracing_config {
    mode = "Active"
  }
  environment {
    variables = {
      PREDICTIONS_STREAM_NAME = var.output_stream_name
      MODEL_BUCKET = var.bucket_name
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

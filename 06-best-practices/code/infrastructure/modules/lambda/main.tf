# Build Lambda Zip
data "archive_file" "lambda_zip" {
    type        = "zip"
    source_file  = "lambda_function.py"   # TODO: change to prediction lambda
    output_path = "lambda_function.zip"
}

resource "aws_lambda_function" "kinesis_lambda" {
  filename      = "lambda_function.zip"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_for_kinesis.arn
  handler       = "lambda_function.lambda_handler"
  runtime = "python3.8"
  tracing_config {
    mode = "Active"
  }
  environment {
    variables = {
      OUTPUT_KINESIS_STREAM = var.output_stream_name
      BUCKET_NAME = var.bucket_name
    }
  }
  timeout = 60
}

resource "aws_lambda_function_event_invoke_config" "kinesis_lambda_event" {
  function_name                = aws_lambda_function.kinesis_lambda.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}

# Create Lambda Event Source Mapping

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

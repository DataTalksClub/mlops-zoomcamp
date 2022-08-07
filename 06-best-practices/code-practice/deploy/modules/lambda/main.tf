resource "aws_lambda_function" "lambda_handler_image" {
  # If the file is not in the current working directory you will need to include a 
  # path.module in the filename.
  image_uri = var.image_uri
  function_name = var.function_name
  package_type = "Image"
  role          = aws_iam_role.iam_for_lambda.arn
  depends_on = [
    var.model_bucket_arn
  ]

  tracing_config {
    mode = "Active"
  }

  environment {
    variables = {
        STREAM_NAME = var.stream_name
    }
  }
  timeout = 100
}

#config for lambda imvoking
resource "aws_lambda_function_event_invoke_config" "lambda_invoke" {
  function_name                = aws_lambda_function.lambda_handler_image.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 1
}

#trigger for lambda
resource "aws_lambda_event_source_mapping" "kinesis_stream_mapping" {
  event_source_arn  = "${var.input_kinesis_stream_arn}"
  function_name     = aws_lambda_function.lambda_handler_image.arn
  starting_position = "LATEST"
  depends_on = [
    aws_iam_role_policy_attachment.kinesis_processing
  ]
}
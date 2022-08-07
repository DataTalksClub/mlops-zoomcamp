resource "aws_iam_role" "iam_for_lambda" {
  name = var.iam_role_name_lambda

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": [
            "lambda.amazonaws.com",
            "kinesis.amazonaws.com"
        ]
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


resource "aws_iam_policy" "allow_kinesis_processing" {
  name        = "allow_kinesis_processing"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "kinesis:ListShards",
        "kinesis:ListStreams",
        "kinesis:*"
      ],
      "Resource": "${var.input_kinesis_stream_arn}",
      "Effect": "Allow"
    },
    {
      "Action": [
        "stream:GetRecord",
        "stream:GetShardIterator",
        "stream:DescribeStream",
        "stream:*"
      ],
      "Resource": "${var.input_kinesis_stream_arn}",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "kinesis_processing" {
    role = aws_iam_role.iam_for_lambda.name
    policy_arn = aws_iam_policy.allow_kinesis_processing.arn
}

resource "aws_iam_role_policy" "inline_lambda_policy" {
    name = "lambdaKinesisInlinePolicy_${var.function_name}"
    role = aws_iam_role.iam_for_lambda.id
    depends_on = [aws_iam_role.iam_for_lambda]
    policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "kinesis:PutRecords",
        "kinesis:PutRecord",
      ],
      "Resource": "${var.output_kinesis_stream_arn}",
      "Effect": "Allow"
    }
  ]
})
}



resource "aws_cloudwatch_log_group" "cloudwatch" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 14
}

resource "aws_iam_policy" "lambda_cloudwatch_logging" {
  name        = "lambda_logging_${var.function_name}"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "cloudwatch_inline_policy" {
    role = aws_iam_role.iam_for_lambda.name
    policy_arn = aws_iam_policy.lambda_cloudwatch_logging.arn
}

resource "aws_iam_role_policy" "inline_s3_polciy" {
    name = "lambdaS3InlinePolicy_${var.function_name}"
    role = aws_iam_role.iam_for_lambda.id
    depends_on = [aws_iam_role.iam_for_lambda]
    policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ListObjectsInBucket",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::${var.model_bucket}"
            ]
        },
        {
            "Sid": "AllObjectActions",
            "Effect": "Allow",
            "Action": "s3:*Object",
            "Resource": [
                "arn:aws:s3:::${var.model_bucket}/*"
            ]
        }
    ]
})
  
}

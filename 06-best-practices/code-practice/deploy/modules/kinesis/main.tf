resource "aws_kinesis_stream" "kinesis_events" {
    name = var.stream_name
    shard_count = var.shard_count
    retention_period = var.retention_period
    shard_level_metrics = var.shard_level_metrics
    tags = {
      "Environment" = "${var.tags}"
    }
}

output "stream_arn" {
    value = aws_kinesis_stream.kinesis_events.arn
}
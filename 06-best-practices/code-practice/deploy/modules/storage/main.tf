resource "aws_s3_bucket" "bucket" {
    bucket = var.bucket 
    tags = {
        Environment = var.tags
    } 
    acl = "private"
}

output "bucket_arn" {
    value = aws_s3_bucket.bucket.arn
}
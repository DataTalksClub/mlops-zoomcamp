resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.bucket_name
  acl    = "private"
  force_destroy = true
}

output "name" {
  value = aws_s3_bucket.s3_bucket.bucket
}

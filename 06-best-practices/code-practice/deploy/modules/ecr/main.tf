resource "aws_ecr_repository" "ecr_repo" {
    name = var.repo_name
    image_tag_mutability = "MUTABLE"

    image_scanning_configuration {
      scan_on_push = false
    }

    force_delete = true
  
}

resource "null_resource" "ecr_image" {
    triggers = {
      python_file = md5(file(var.lambda_function_local_path))
      docker_file = md5(file(var.docker_image_local_path))
    }

    provisioner "local-exec" {
        command = <<EOF
        aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${var.account_id}.dkr.ecr.${var.region}.amazonaws.com
        cd ../
        docker build --build-arg STREAM_NAME_ARG=${var.stream_name} --build-arg RUN_ID_ARG=${var.run_id} --build-arg TEST_RUN_ARG=${var.test_run} --build-arg MODEL_BUCKET_ARG=${var.model_bucket} -t ${aws_ecr_repository.ecr_repo.repository_url}:${var.ecr_image_tag} .
        docker push ${aws_ecr_repository.ecr_repo.repository_url}:${var.ecr_image_tag}
        EOF
    }
    depends_on = [
        aws_ecr_repository.ecr_repo
    ]
}

data aws_ecr_image lambda_image{
    depends_on = [
        null_resource.ecr_image
    ]
    repository_name = var.repo_name
    image_tag = var.ecr_image_tag
}

output "image_uri" {
    value = "${aws_ecr_repository.ecr_repo.repository_url}:${data.aws_ecr_image.lambda_image.image_tag}"
}

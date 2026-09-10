---
video_url: "https://www.youtube.com/watch?v=OMwwZ0Z_cdk&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=52"
code:
  - label: "Best-practices project code"
    path: code/README.md
---

# CI/CD: Introduction

Continuous integration and continuous delivery automate the path from a code change to a tested and deployed service. CI validates a change. CD delivers an approved change to the target environment.

## The workflow design

The course pipeline runs unit tests, integration tests, and a Terraform plan during integration. The delivery workflow applies Terraform, builds and pushes the Docker image to ECR, and updates the Lambda service.

![The complete CI/CD workflow for the ride-prediction service](ci_cd_zoomcamp.png)

The workflow files live under `.github/workflows/`. Pull requests should run the checks that protect the shared branch. A controlled push or merge can start delivery after CI passes.

![The CI/CD architecture in the project](images/11-cicd-introduction-02-repository.jpg)

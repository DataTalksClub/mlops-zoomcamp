# Module 6: Best Practices

We make the deployed model easier to test, review, provision, and deliver. We move from Python tests through Terraform and GitHub Actions.

## 6.1 [Testing Python Code with pytest](01-pytest.md)

Separate model logic from cloud clients and cover the service with fast unit tests.

## 6.2 [Integration Tests with docker-compose](02-docker-compose-tests.md)

Start the service in Docker and verify its HTTP API with a deterministic test event.

## 6.3 [Testing Cloud Services with LocalStack](03-localstack.md)

Exercise Kinesis-compatible behavior locally without creating real AWS resources.

## 6.4 [Code Quality: Linting and Formatting](04-linting-formatting.md)

Use isort, Black, and Pylint to keep code consistent and catch common problems.

## 6.5 [Git Pre-commit Hooks](05-pre-commit.md)

Run project checks automatically before creating a commit.

## 6.6 [Makefiles and make](06-makefiles.md)

Give tests, quality checks, builds, and deployment steps stable command names.

## 6.7 [Terraform: Introduction](07-terraform-introduction.md)

Describe the AWS stream-based prediction infrastructure as version-controlled code.

## 6.8 [Terraform: Modules and Output Variables](08-terraform-modules.md)

Extract reusable infrastructure and pass resource identifiers between modules.

## 6.9 [Build an End-to-end Ride Prediction Workflow](09-terraform-pipeline.md)

Connect Kinesis, Lambda, S3, and ECR into a deployable prediction workflow.

## 6.10 [Test the Pipeline End to End](10-terraform-testing.md)

Send a ride event through the deployed pipeline and review the prediction output.

## 6.11 [CI/CD: Introduction](11-cicd-introduction.md)

Map pull-request checks and delivery jobs onto the ride-prediction architecture.

## 6.12 [Continuous Integration](12-continuous-integration.md)

Run tests and Terraform plan automatically for proposed changes.

## 6.13 [Continuous Delivery](13-continuous-delivery.md)

Build, publish, and deploy the service after an approved change.

## Homework

More information is available in the [Module 6 homework](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/cohorts/2025/06-best-practices/homework.md).

## Code and resources

Resources:

- [Best-practices code](code)
- [Terraform concepts and references](docs/extra-material.md)
- [AWS stream-pipeline source diagram](AWS-stream-pipeline.png)
- [CI/CD source diagram](ci_cd_zoomcamp.png)

Cloud resources can incur charges. Destroy temporary infrastructure after testing and keep credentials out of the repository.

## Community Notes

Share community notes and resources below.

* [Week 6a notes by M. Ayoub C.](https://gist.github.com/Qfl3x/267d4cff36b58de67b4e33ca3fc9983f)
* [Unit tests, integration tests, LocalStack, code quality, pre-commit, and Makefile notes by Hongfan](https://github.com/Muhongfan/MLops/blob/main/06-best-practice/README.md)
* [Week 6 notes from 2023](https://github.com/dimzachar/mlops-zoomcamp/tree/master/notes/Week_6)
* [2025 best-practices notes and FAQ by Nitin Gupta](https://github.com/niting9881/course-mlops-zoomcamp/blob/main/06-best-practices/README.md)
* [Week 6 detailed notes by Muhammad Shifa](https://github.com/MuhammadShifa/mlops-zoomcamp2025/blob/main/06-best-practices/code/README.md)
* Send a PR, add your notes above this line

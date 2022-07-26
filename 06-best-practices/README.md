# 6. Best Practices

## Part A

(Part B below)

### 6.1 Testing Python code with pytest

<a href="https://www.youtube.com/watch?v=CJp1eFQP5nk&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-6-1.jpg">
</a>


### 6.2 Integration tests with docker-compose

<a href="https://www.youtube.com/watch?v=lBX0Gl7Z1ck&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-6-2.jpg">
</a>


### 6.3 Testing cloud services with LocalStack

<a href="https://www.youtube.com/watch?v=9yMO86SYvuI&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-6-3.jpg">
</a>


### 6.4 Code quality: linting and formatting

<a href="https://www.youtube.com/watch?v=uImvWE-iSDQ&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-6-4.jpg">
</a>


### 6.5 Git pre-commit hooks

<a href="https://www.youtube.com/watch?v=lmMZ7Axk2T8&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-6-5.jpg">
</a>


### 6.6 Makefiles and make

<a href="https://www.youtube.com/watch?v=F6DZdvbRZQQ&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-6-6.jpg">
</a>

### 6.7 Homework

More information here: [homework.md](homework.md)

### Notes

Did you take notes? Add them here:

* [Week 6a Notes by M. Ayoub C.](https://gist.github.com/Qfl3x/267d4cff36b58de67b4e33ca3fc9983f)
* Send a PR, add your notes above this line

<br>

## Part B

### Infrastructure-as-Code
with Terraform 

![image](AWS-stream-pipeline.png)

#### Summary
Setting up a stream-based pipeline infrastructure in AWS, using Terraform

#### Project infrastructure modules:
* Amazon Web Service (AWS):
    * Kinesis: Streams (Producer & Consumer)
    * Lambda: Serving API
    * S3 Bucket: Model artifacts
    * ECR: Image Registry

#### 6B.1: Terraform - Introduction

<a href="https://www.youtube.com/watch?v=zRcLgT7Qnio&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=48">
  <img src="images/AWS-stream-pipeline.png">
</a>

* Introduction
* Setup & Pre-Reqs
* Concepts of Terraform and IaC (reference material from previous courses)

#### 6B.2: Terraform - Modules and Outputs variables

<a href="https://www.youtube.com/watch?v=-6scXrFcPNk&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=49">
  <img src="images/AWS-stream-pipeline.png">
</a>

* What are they?
* Creating a Kinesis module

#### 6B.3: Build an e2e workflow for Ride Predictions

<a href="https://www.youtube.com/watch?v=JVydd1K6R7M&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=50">
  <img src="images/AWS-stream-pipeline.png">
</a>

* TF resources for ECR, Lambda, S3

#### 6B.4: Test the pipeline e2e

* Demo: apply TF to our use-case, manually deploy data dependencies & test
* Recap: IaC, Terraform, next steps

#### Setup

**Installation**:

* [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) (both versions are fine)
* [terraform client](https://www.terraform.io/downloads)

**Configuration**:

1. If you've already created an AWS account, head to the IAM section, generate your secret-key, and download it locally. 
[Instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-prereqs.html)

2. [Configure]((https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)) `aws-cli` with your downloaded AWS secret keys:
      ```shell
         $ aws configure
         AWS Access Key ID [None]: xxx
         AWS Secret Access Key [None]: xxx
         Default region name [None]: eu-west-1
         Default output format [None]:
      ```

3. Verify aws config:
      ```shell
        $ aws sts get-caller-identity
      ```

4. (Optional) Configuring with `aws profile`: [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sourcing-external.html) and [here](https://registry.terraform.io/providers/hashicorp/aws/latest/docs#using-an-external-credentials-process) 

<br>

Additional material on understanding Terraform concepts: [here](docs.md)

<br>

### CI/CD
with GitHub Actions

![image](ci_cd_zoomcamp.png)

#### 6B.5: CI/CD - Introduction
* Architecture (Ride Predictions)
* What are GitHub workflows?

#### 6B.6: Continuous Integration
* `ci-tests.yml`
    * Automate sections from tests: Env setup, Unit test, Integration test, Terraform plan
    * Create a CI for `on-pull-request` to `develop` branch
    * Execute demo

#### 6B.7: Continuous Delivery
* `cd-deploy.yml`
    * Automate sections from tests: Terraform plan, Terraform apply, Docker build & ECR push, Update Lambda config
    * Create a CI for `on-push-to` to `develop` branch
    * Execute demo
    
<br>

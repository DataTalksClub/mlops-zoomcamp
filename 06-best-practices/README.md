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


### 6.X Homework


More information here: [homework.md](homework.md)

<br>

## Part B

### 6.7 Infrastructure as Code

#### Project infrastructure modules:
* Amazon Web Service (AWS):
    * Kinesis: Streams (Producer & Consumer)
    * Lambda: Serving API
    * S3 Bucket: Model artifacts
    * ECR: Image Registry
    
![image](AWS-stream-pipeline.png)


#### Summary
Setting up a stream-based pipeline infrastructure in AWS, using Terraform

1. Video 1: Terraform - Introduction
    * Introduction
    * Setup & Pre-Reqs
    * Concepts of Terraform and IaC (reference material from previous courses)

2. Video 2: Terraform - Modules and Outputs variables
    * What are they?
    * Creating a Kinesis module

3. Video 3: Build an e2e workflow for Ride Predictions
    * TF resources for ECR, Lambda, S3

4. Video 4: Test the pipeline e2e
    * Demo: apply TF to our use-case, manually deploy data dependencies & test
    (This video is TBD)


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

#### Concepts of Terraform and IaC
(refer to previous videos, links in README)

1. For an introduction to Terraform and IaC concepts, please refer to [this video](https://www.youtube.com/watch?v=Hajwnmj0xfQ&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=11) 
(from the DE Zoomcamp), especially the sections in the time-codes:

    * 00:00 Introduction
    * 00:35 What is Terraform?
    * 01:10 What is IaC?
    * 01:43 Advantages of IaC
    * 14:48 Installing Terraform
    * 02:28 More on Installing Terraform

2. For a quickstart tutorial, and understanding the main components of a basic Terraform script, please refer to [this video](https://www.youtube.com/watch?v=dNkEgO-CExg&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=12)
    (from the DE Zoomcamp). Please note that this example uses GCP as a cloud provider, while for MLOps Zoomcamp we are using AWS.
    
    * 00:00 Introduction
    * 00:20 .terraform-version
    * 01:04 main.tf
    * 01:23 terraform declaration
    * 03:25 provider plugins
    * 04:00 resource example - google_storage_bucket
    * 05:42 provider credentials
    * 06:34 variables.tf
    * 10:54 overview of terraform commands
    * 13:35 running terraform commands
    * 18:08 recap

<br>

### CI/CD
CI/CD w/ GitHub Actions

* What are GitHub workflows?
* `test-pr-pipeline.yml`
    * Automate sections from tests: Env setup, Unit test, Integration test, Terraform plan
    * Create a CI for `on-pull-request` to `develop` branch
    * Execute demo

* `deploy-pipeline.yml`
    * Automate sections from tests: Terraform plan, Terraform apply, Docker build & ECR push, Update Lambda config
    * Create a CI for `on-push-to` to `develop` branch
    * Execute demo
    
<br>

**Other material:**

Deploying Serverless Machine Learning with AWS (one of my previous videos explaining Lambda integration with Docker images): https://www.youtube.com/watch?v=79B8AOKkpho&t=689s 



## Notes

Did you take notes? Add them here:

* Send a PR, add your notes above this line

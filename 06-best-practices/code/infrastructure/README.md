## GCP Overview

### Project infrastructure modules in GCP:
* Amazon Web Service (AWS):
    * S3 Bucket: artifacts
    * Lambda: Serving API
    * Kinesis: Streams (Producer & Consumer)

### Setup

1. If you've already created an AWS account, head to the IAM section, generate your secret-key, and download it locally. 
[Instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-prereqs.html)
2. Download [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) as a tool to use on your terminal
3. Check installation
  ```bash
    $ which aws
    /usr/local/bin/aws 
    $ aws --version
    aws-cli/2.x Python/3.x Darwin/18.x botocore/2.x
  ```
4. [Configure]((https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)) `aws-cli` with your downloaded AWS secret keys:
  ```shell
   $ aws configure
     AWS Access Key ID [None]: xxx
     AWS Secret Access Key [None]: xxx
     Default region name [None]: eu-west-1
     Default output format [None]:
  ```
5. Verify aws config:
  ```shell
   $ aws sts get-caller-identity
  ```
 
### Terraform

(Content: TBD)

1. To create infra
```bash
terraform init
terraform plan
terraform apply
```

2. To test:
```bash
aws kinesis put-record --stream-name source_kinesis_stream --partition-key 123 --data "Hello, this is a test."
```
And then check on CloudWatch logs. Unfortunately `get-records` on `output_kinesis_stream` will not always work
(unless you're willing to loop through all the `next_iterators`)

![image](cw_log_output.png)

### Pending

1. Remove test lambda and replace with prediction lambda
```bash
data "archive_file" -> source_file = "${path.module}/../
```

2. Stage-based infra
```bash
terraform [init | plan | apply ] -var-file="vars/dev.tfvars"
terraform [init | plan | apply ] -var-file="vars/prod.tfvars"
```

3. Testing with localstack ? (if time permits, or homework)
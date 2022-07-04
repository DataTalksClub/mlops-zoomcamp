## IaC w/ Terraform

### Project infrastructure modules:
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

1. To create infra (manually, in order to test on staging env)
   ```bash
   terraform init
   terraform plan -var-file=vars/stg.tfvars
   terraform apply -var-file=vars/stg.tfvars
   ```

2. Make a copy of `.env_template` and generate shared env-vars 
    ```bash
    cp ../.env_template ../.env
    . ../.env
    ```

3. To prepare aws env (copy model artifacts, set env-vars for lambda etc.):
    ```
    . ./deploy_manual.sh
    ```

4. To test the pipeline end-to-end with our new cloud infra:
    ```
    . ./test_cloud_e2e.sh
    ``` 

5. And then check on CloudWatch logs. Or try `get-records` on the `output_kinesis_stream` (refer to `integration_test`)

![image](cw_logs_lambda.png)


### Pending

1. Unfortunately, the `RUN_ID` set via the `ENV` or `ARG` in `Dockerfile`, disappears during lambda invocation.
Had to set it via `aws lambda update-function-configuration` cli command (refer to `deploy_manual.sh`)

2. CI/CD
- In principle, explain:
    - generate metrics offline -> set env vars for lambda w/ stage-based deployments
    - train_pipeline -> model registry & update run_id
    - In practice, change in mlflow / db -> get curr run_id
    
3. pass working-dir as arg into `integration-test/run.sh` (required for ci/cd)

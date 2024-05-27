# 3.5 Deploying: Running operations in production


## 1. Permissions

### Videos

1. [Configure permissions on AWS](https://youtu.be/TgdFaf4mw38)

### Code

-   [`custom/permissions.py` block](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/custom/permissions.py)

---

## 2. Deploy

### Videos

1. [Setup and deploy using Terraform](https://youtu.be/w9zl3n2a3Wc)

### Code

-   [`custom/infrastructure_setup.py` block](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/custom/infrastructure_setup.py)
-   [`custom/deploy.py` block](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/custom/deploy.py)
-   [`custom/teardown_deployed_resources.py` block](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/custom/teardown_deployed_resources.py)

---

## 3. Continuous deployment and integration

### Videos

1. [CI/CD with GitHub Actions](https://youtu.be/tPkA3WjLSHE)
1. [Mage deployed](https://youtu.be/DMV2zEM50jY)

### Code

-   [`custom/ci_and_cd.py` block](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/custom/ci_and_cd.py)

## Code

1. [Deployment pipeline `metadata.yaml`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/pipelines/deploying_to_production/metadata.yaml)

---

## Resources

1. [Repository setup](https://docs.mage.ai/production/ci-cd/local-cloud/repository-setup)
1. AWS IAM policy permissions

    1. [Terraform apply](https://docs.mage.ai/production/deploying-to-cloud/aws/terraform-apply-policy)
    1. [Terraform destroy](https://docs.mage.ai/production/deploying-to-cloud/aws/terraform-destroy-policy)

1. [Terraform setup](https://docs.mage.ai/production/deploying-to-cloud/using-terraform)

1. [Configure Terraform for AWS](https://docs.mage.ai/production/deploying-to-cloud/aws/setup)

1. [CI/CD overview](https://docs.mage.ai/production/ci-cd/overview)

1. [Setup GitHub actions for CI/CD](https://docs.mage.ai/production/ci-cd/local-cloud/github-actions#github-actions-setup)

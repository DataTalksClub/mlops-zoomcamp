## Extra Material

### Concepts of IaC and Terraform

#### Summary

**Infrastructure-as-Code (IaC)**:
* Define and automate operations around you application's infrastructure.
* Can use version control to track changes made to infrastructure
* Easy to replicate the configuration across different environments such as development, staging, and production. 


#### Reference Material

We have already covered Terraform concepts at a deeper level in the [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp), and will not be repeating some of those basic concepts again. You can find the content here for your reference:

**Notes**:
* [Terraform Overview](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_1_basics_n_setup/1_terraform_gcp/1_terraform_overview.md)

**Videos**:

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

In case you're using GCP instead of AWS, following is some setup material:
* [Local Setup for Terraform and GCP](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_1_basics_n_setup/1_terraform_gcp)
* [GCP Overview](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_1_basics_n_setup/1_terraform_gcp/2_gcp_overview.md)
* [main.tf](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_1_basics_n_setup/1_terraform_gcp/terraform/main.tf)

#### References
* Terraform with AWS: [Getting Started](https://learn.hashicorp.com/collections/terraform/aws-get-started) and [AWS provider library](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
* Terraform Modules: [Define](https://www.terraform.io/language/modules/develop) and [Call](https://www.terraform.io/language/modules/syntax)


### Concepts of CI/CD and GitHub Actions

#### Summary
* Using GitHub Actions to create workflows to automatically test a pull request, 
build and push a Docker image, and deploy the updated lambda service to production. 
* Creating specific YAML files in GitHub repo, to automatically kick off a series of automation steps.
* Motivation on automating your further tasks with GitHub Actions:
    * Orchestrating a continuous training pipeline (CT) to retrain your model and generate updated model artifacts in production
    * Integrating the model registry (MLflow, DVC etc.) to fetch the latest model version or experiment ID
    * and many more... 


#### Reference Material
* [GitHub Actions & Workflows](https://docs.github.com/en/actions/using-workflows)
* [Build-Push image to ECR](https://docs.github.com/en/actions/deployment/deploying-to-your-cloud-provider/deploying-to-amazon-elastic-container-service)
* [Python tests](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)

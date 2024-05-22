## Course Project

### Objective

The goal of this project is to apply everything we have learned
in this course to build an end-to-end machine learning project.

## Problem statement

For the project, we will ask you to build an end-to-end ML project. 

For that, you will need:

* Select a dataset that you're interested in (see [Datasets](#datasets))
* Train a model on that dataset tracking your experiments
* Create a model training pipeline
* Deploy the model in batch, web service or streaming
* Monitor the performance of your model
* Follow the best practices 


## Technologies 

You don't have to limit yourself to technologies covered in the course. You can use alternatives as well:

* **Cloud**: AWS, GCP, Azure, ... 
* **Experiment tracking tools**: MLFlow, Weights & Biases, ... 
* **Workflow orchestration**: Prefect, Airflow, Flyte, Kubeflow, Argo, ...
* **Monitoring**: Evidently, WhyLabs/whylogs, ...
* **CI/CD**: Github actions, Gitlab CI/CD, ...
* **Infrastructure as code (IaC)**: Terraform, Pulumi, Cloud Formation, ...

If you use a tool that wasn't covered in the course, be sure to explain what that tool does.

If you're not certain about some tools, ask in Slack.

## Peer reviewing

> [!IMPORTANT]  
> To evaluate the projects, we'll use peer reviewing. This is a great opportunity for you to learn from each other.
> * To get points for your project, you need to evaluate 3 projects of your peers
> * You get 3 extra points for each evaluation

## Evaluation Criteria

* Problem description
    * 0 points: The problem is not described
    * 1 point: The problem is described but shortly or not clearly 
    * 2 points: The problem is well described and it's clear what the problem the project solves
* Cloud
    * 0 points: Cloud is not used, things run only locally
    * 2 points: The project is developed on the cloud OR uses localstack (or similar tool) OR the project is deployed to Kubernetes or similar container management platforms
    * 4 points: The project is developed on the cloud and IaC tools are used for provisioning the infrastructure
* Experiment tracking and model registry
    * 0 points: No experiment tracking or model registry
    * 2 points: Experiments are tracked or models are registered in the registry
    * 4 points: Both experiment tracking and model registry are used
* Workflow orchestration
    * 0 points: No workflow orchestration
    * 2 points: Basic workflow orchestration
    * 4 points: Fully deployed workflow 
* Model deployment
    * 0 points: Model is not deployed
    * 2 points: Model is deployed but only locally
    * 4 points: The model deployment code is containerized and could be deployed to cloud or special tools for model deployment are used
* Model monitoring
    * 0 points: No model monitoring
    * 2 points: Basic model monitoring that calculates and reports metrics
    * 4 points: Comprehensive model monitoring that sends alerts or runs a conditional workflow (e.g. retraining, generating debugging dashboard, switching to a different model) if the defined metrics threshold is violated
* Reproducibility
    * 0 points: No instructions on how to run the code at all, the data is missing
    * 2 points: Some instructions are there, but they are not complete OR instructions are clear and complete, the code works, but the data is missing
    * 4 points: Instructions are clear, it's easy to run the code, and it works. The versions for all the dependencies are specified.
* Best practices
    * [ ] There are unit tests (1 point)
    * [ ] There is an integration test (1 point)
    * [ ] Linter and/or code formatter are used (1 point)
    * [ ] There's a Makefile (1 point)
    * [ ] There are pre-commit hooks (1 point)
    * [ ] There's a CI/CD pipeline (2 points)

> [!NOTE]
> It's highly recommended to create a new repository for your project (not inside an existing repo) with a meaningful title, such as
> "Car Price Prediction" or "Music Genre Classification" and include as many details as possible in the README file. ChatGPT can assist you with this. Doing so will not only make it easier to showcase your project for potential job opportunities but also have it featured on the [Projects Gallery App](#projects-gallery).
> If you leave the README file empty or with minimal details, there may be point deductions as per the [Evaluation Criteria](#evaluation-criteria).

## Resources

### Datasets

Refer to the provided [datasets](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/projects/datasets.md) for possible selection.

### Projects Gallery

Explore a collection of projects completed by members of our community. The projects cover a wide range of topics and utilize different tools and techniques. Feel free to delve into any project and see how others have tackled real-world problems with data, structured their code, and presented their findings. It's a great resource to learn and get ideas for your own projects.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://datatalksclub-projects.streamlit.app/)

### MLOps Zoomcamp 2023

* [2023 Projects](../cohorts/2023/07-project)

### MLOps Zoomcamp 2022

* [2022 Projects](../cohorts/2022/07-project)



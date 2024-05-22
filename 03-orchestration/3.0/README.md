# 3.0 Introduction: ML pipelines and Mage

## What is MLOps

Operationalizing ML models involves moving them from development to production to drive business value.

1. Preparing the model for deployment involves optimizing performance, ensuring it handles real-world data, and packaging it for integration into existing systems.
2. Deploying the model involves moving it from development to production, making it accessible to users and applications.
3. Once deployed, models must be continuously monitored for accuracy and reliability, and may need retraining on new data and updates to maintain effectiveness.
4. The operationalized model must be integrated into existing workflows, applications, and decision-making processes to drive business impact.

Effective operationalization enables organizations to move beyond experimentation and drive tangible value from ML at scale, powering intelligent applications that personalize the customer experience and creates real business value.

## Why we need to operationalize ML

### Productivity

MLOps fosters collaboration between data scientists, ML engineers, and DevOps teams by providing a unified environment for experiment tracking, feature engineering, model management, and deployment. This breaks down silos and accelerates the entire machine learning lifecycle.

### Reliability

MLOps ensures high-quality, reliable models in production through clean datasets, proper testing, validation, CI/CD practices, monitoring, and governance.

### Reproducibility

MLOps enables reproducibility and compliance by versioning datasets, code, and models, providing transparency and auditability to ensure adherence to policies and regulations.

### Time-to-value

MLOps streamlines the ML lifecycle, enabling organizations to successfully deploy more projects to production and derive tangible business value and ROI from AI/ML investments at scale.

## How Mage helps MLOps

### Data preparation

Mage offers features to build, run, and manage data pipelines for data transformation and integration, including pipeline orchestration, notebook environments, data integrations, and streaming pipelines for real-time data.

### Training and deployment

Mage helps prepare data, train machine learning models, and deploy them with accessible API endpoints.

### Standardize complex processes

Mage simplifies MLOps by providing a unified platform for data pipelining, model development, deployment, versioning, CI/CD, and maintenance, allowing developers to focus on model creation while improving efficiency and collaboration.

## Example data pipeline

If you haven’t setup your project yet, please refer to the quickstart guide at the root of module 3.

1. Open [`http://localhost:6789`](http://localhost:6789) in your browser.

1. In the top left corner of the screen next to the Mage logo and **`mlops`** project name,
   click the project selector dropdown and choose the **`unit_0_setup`** option.

1. Click on the pipeline named **`example_pipeline`**.
1. Click on the button labeled **`Run @once`**.

[Code for example data pipeline](https://github.com/mage-ai/mlops/tree/master/mlops/unit_0_setup)

## The definitive end-to-end machine learning (ML lifecycle) guide and tutorial for data engineers

Read more about ML and MLOps [here](https://mageai.notion.site/The-definitive-end-to-end-machine-learning-ML-lifecycle-guide-and-tutorial-for-data-engineers-ea24db5e562044c29d7227a67e70fd56?pvs=4).

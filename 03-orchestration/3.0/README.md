# 3.0 Introduction: ML pipelines and Mage

# What is MLOps

> Operationalizing ML models involves moving them from development to production to drive business value.

## 1. Preparing the model for deployment involves optimizing performance, ensuring it handles real-world data, and packaging it for integration into existing systems.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-prepare2.png?raw=true)

## 2. Deploying the model involves moving it from development to production, making it accessible to users and applications.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-deploy.png?raw=true)

## 3. Once deployed, models must be continuously monitored for accuracy and reliability, and may need retraining on new data and updates to maintain effectiveness.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-retrain.png?raw=true)

## 4. The operationalized model must be integrated into existing workflows, applications, and decision-making processes to drive business impact.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-ops.png?raw=true)

---

> Effective operationalization enables organizations to move beyond experimentation and drive tangible value from ML at scale, powering intelligent applications that personalize the customer experience and creates real business value.

---

# Why we need to operationalize ML

## 1. Productivity

MLOps fosters collaboration between data scientists, ML engineers, and DevOps teams by providing a unified environment for experiment tracking, feature engineering, model management, and deployment. This breaks down silos and accelerates the entire machine learning lifecycle.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-collaboration.png?raw=true)

## 2. Reliability

MLOps ensures high-quality, reliable models in production through clean datasets, proper testing, validation, CI/CD practices, monitoring, and governance.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-reliability.png?raw=true)

## 3. Reproducibility

MLOps enables reproducibility and compliance by versioning datasets, code, and models, providing transparency and auditability to ensure adherence to policies and regulations.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-reproduce.png?raw=true)

## 4. Time-to-value

MLOps streamlines the ML lifecycle, enabling organizations to successfully deploy more projects to production and derive tangible business value and ROI from AI/ML investments at scale.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-value.png?raw=true)

---

# How Mage helps MLOps

## 1. Data preparation

Mage offers features to build, run, and manage data pipelines for data transformation and integration, including pipeline orchestration, notebook environments, data integrations, and streaming pipelines for real-time data.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-mage-data.png?raw=true)

## 2. Training and deployment

Mage helps prepare data, train machine learning models, and deploy them with accessible API endpoints.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-mage-training.png?raw=true)

## 3. Standardize complex processes

Mage simplifies MLOps by providing a unified platform for data pipelining, model development, deployment, versioning, CI/CD, and maintenance, allowing developers to focus on model creation while improving efficiency and collaboration.

![](https://github.com/mage-ai/assets/blob/main/mlops/0-mage-standard.png?raw=true)

---

# Example data pipeline

<a href="https://youtu.be/7hKrQmoARD8">
  <img src="https://github.com/mage-ai/assets/blob/main/mlops/0-prepare.png?raw=true">
</a>

> [Click image play video](https://youtu.be/7hKrQmoARD8)

If you haven’t setup your project yet, please refer to the [quickstart guide](../README.md#Quickstart) or follow these steps:

1. Clone the following respository containing the complete code for this module:

    ```
    git clone https://github.com/mage-ai/mlops.git
    ```

1. Change directory into the cloned repo:

    ```
    cd mlops
    ```

1. Launch Mage and the database service (PostgreSQL):

    ```
    ./scripts/start.sh
    ```

1. The subproject that contains all the pipelines and code is named
   [`unit_3_observability`](https://github.com/mage-ai/mlops/tree/master/mlops/unit_3_observability)

## Run example pipeline

1. Open [`http://localhost:6789`](http://localhost:6789) in your browser.

1. In the top left corner of the screen next to the Mage logo and **`mlops`** project name,
   click the project selector dropdown and choose the **`unit_0_setup`** option.

1. Click on the pipeline named **`example_pipeline`**.
1. Click on the button labeled **`Run @once`**.

## Resources

1. [Code for example data pipeline](https://github.com/mage-ai/mlops/tree/master/mlops/unit_0_setup)
1. [The definitive end-to-end machine learning (ML lifecycle) guide and tutorial for data engineers](https://mageai.notion.site/The-definitive-end-to-end-machine-learning-ML-lifecycle-guide-and-tutorial-for-data-engineers-ea24db5e562044c29d7227a67e70fd56?pvs=4).

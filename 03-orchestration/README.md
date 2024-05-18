# 3. Orchestration and ML Pipelines

## 3.0 Introduction: ML pipelines and Mage

- What is MLOps
- Why we need to operationalize ML
- How Mage helps MLOps
- Example data pipeline

## 3.1 Data preparation: ETL and feature engineering

- Ingest raw data
- Prepare data for training
- Build training sets
- Data validations using built-in testing framework

## 3.2 Training: sklearn models and XGBoost

- Reusable training set data product
- Training pipeline for sklearn models
- Training pipeline for XGBoost
- Tracking training metrics with experiments

## 3.3 Observability: Monitoring and alerting

- Dashboard for sklearn training pipeline health
- Dashboard for XGBoost model explainability
- Dashboard for model training performance
- Alerts for pipeline runs

## 3.4 Triggering: Inference and retraining

- Automatic retraining pipeline
- No-code UI input fields to interact with models
- Inference pipeline for real-time predictions

## 3.5 Deploying: Running operations in production

- Setup AWS permissions and credentials
- Terraform setup
- Initial deployment to AWS
- Use GitHub Actions for CI/CD to automate deployment to production

## Quickstart

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

# Notes previous editions

- [2022 Prefect notes](../cohorts/2022/03-orchestration/README.md)
- [2023 Prefect notes](../cohorts/2023/03-orchestration/prefect/README.md)

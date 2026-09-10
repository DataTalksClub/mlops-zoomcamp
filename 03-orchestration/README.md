# Module 3: Orchestration and ML Pipelines

We turn the duration prediction notebook into a repeatable, parameterized training script and then connect it to the concepts of workflow orchestration.

## 3.1 [Introduction to ML Pipelines](01-ml-pipelines.md)

Define a training pipeline, make its dependencies explicit, and distinguish pipeline logic from orchestration.

## 3.2 [Turning the Notebook into a Python Script](02-notebook-to-script.md)

Refactor the notebook into functions, expose the training period as command-line parameters, and preserve MLflow metadata.

## 3.3 [Using an Orchestrator](03-orchestrator.md)

Schedule, parameterize, backfill, and optionally deploy the training workflow with an orchestrator.

## Homework

More information is available in the [Module 3 homework](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/cohorts/2025/03-orchestration/homework.md).

## Optional resources

MLflow

To run MLflow with Docker, create an `mlflow.dockerfile`:

```dockerfile
FROM python:3.10-slim

RUN pip install mlflow==2.12.1

EXPOSE 5000

CMD [ \
    "mlflow", "server", \
    "--backend-store-uri", "sqlite:///home/mlflow_data/mlflow.db", \
    "--host", "0.0.0.0", \
    "--port", "5000" \
]
```

Add it to `docker-compose.yaml` and persist the MLflow data directory:

```yaml
  mlflow:
    build:
      context: .
      dockerfile: mlflow.dockerfile
    ports:
      - "5000:5000"
    volumes:
      - "${PWD}/mlflow_data:/home/mlflow_data/"
```

Use the same MLflow version in the training environment. The service should then be reachable at `http://localhost:5000` from the host or at `http://mlflow:5000` from another Compose service.

## Community Notes

Share community notes and resources below.

Previous-edition notes:

- [2022 Prefect notes](https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/cohorts/2022/03-orchestration)
- [2023 Prefect notes](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/cohorts/2023/03-orchestration/prefect/README.md)
- [2024 Mage notes](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/cohorts/2024/03-orchestration/README.md)

2025 notes:

* [Running Airflow + MLflow using Docker by André Calatré](https://github.com/calatre/mlops-zoomcamp/tree/main/03-orchestration)
* [Week 3 workflow orchestration and Prefect by hannarud](https://github.com/hannarud/mlops-zoomcamp-2025/blob/main/week3_notes.md)
* [Orchestration with Prefect notes and code by Muhammad Shifa](https://github.com/MuhammadShifa/mlops-zoomcamp2025/blob/main/03-orchestration/README.md)
* Send a PR, add your notes above this line

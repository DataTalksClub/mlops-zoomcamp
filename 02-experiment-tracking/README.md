# Module 2: Experiment Tracking and Model Management

We record experiments from the taxi duration notebook and follow a model from its first run to a shared registry. We use MLflow for local tracking and model management. We also set up a remote AWS server.

## 2.1 [Experiment Tracking Intro](01-experiment-tracking-intro.md)

Define the tracking concepts and understand why we keep them together.

## 2.2 [Getting Started with MLflow](02-mlflow-getting-started.md)

Install MLflow, start the local UI, configure SQLite, and connect the notebook to an experiment.

## 2.3 [Experiment Tracking with MLflow](03-experiment-tracking.md)

Track hyperparameter search runs, then compare their parameters and metrics.

## 2.4 [Model Management](04-model-management.md)

Keep selected model artifacts and their lineage after the experiment ends.

## 2.5 [Model Registry](05-model-registry.md)

Register model versions, review lineage, and coordinate promotion with the deployment process.

## 2.6 [MLflow in Practice](06-mlflow-in-practice.md)

Choose between local tracking and a shared server with database-backed metadata and S3 artifacts.

## 2.7 [MLflow: Benefits, Limitations and Alternatives](07-mlflow-alternatives.md)

Evaluate the trade-offs of MLflow and compare the requirements that matter when choosing a tracking platform.

## Homework

More information is available in the [Module 2 homework](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/cohorts/2025/02-experiment-tracking/homework.md).

## Optional resources

Use these links to explore the presentation, AWS setup, and current MLflow documentation.

- [Slides](https://drive.google.com/file/d/1YtkAtOQS3wvY7yts_nosVlXrLQBq5q37/view?usp=sharing)
- [MLflow on AWS](docs/mlflow_on_aws.md)
- [MLflow documentation](https://mlflow.org/docs/latest/)

Use `search_experiments` in current MLflow versions instead of `list_experiments`, and follow [the MLflow issue](https://github.com/mlflow/mlflow/issues/8941) when you update older notebooks.

## Community Notes

Share community notes and resources below.

* [Notes and general MLflow documentation by Ayoub](https://gist.github.com/Qfl3x/ccff6b0708358c040e437d52af0c2e43)
* [Minimalist MLflow code reference by Anna V](https://github.com/annnvv/mlops_zoomcamp/blob/main/notes/module2_notes_MLflow.md)
* [Notes from the second lesson by Neimv](https://gitlab.com/neimv/mlops/-/blob/main/lessons_weeks/notes_2.md)
* [Experiment tracking notes by Ayoub B](https://github.com/ayoub-berdeddouch/mlops-journey/blob/main/experiment_tracking_02.md)
* [Experiment tracking by particle1331](https://particle1331.github.io/ok-transformer/nb/mlops/03-mlflow.html)
* [Week 2 experiment tracking notes by Bengsoon Chuah](https://github.com/bengsoon/mlops-zoomcamp/blob/main/02-experiment-tracking/notes/Experiment_Tracking_notes.md)
* [Model management notes by Alvaro Pena](https://github.com/alvarofps/mlops-zoomcamp/blob/main/02-experiment-tracking/my-notes/2.4%20Model%20management.md)
* [Notes by Alvaro Navas](https://github.com/ziritrion/mlopszoomcamp/blob/main/notes/2_experiment.md)
* [Notebook by froukje](https://github.com/froukje/ml-ops-zoomcamp/blob/master/02-experiment-tracking/week02.ipynb) and [notes](https://medium.com/@falbrechtg/getting-started-with-mlflow-tracking-46a0089d6a73)
* [MLflow on GCP by Isaac Kargar](https://kargarisaac.github.io/blog/mlops/data%20engineering/2022/06/15/MLFlow-on-GCP.html)
* [Week 2 experiment tracking notes by Bhagabat](https://github.com/BPrasad123/MLOps_Zoomcamp/tree/main/Week2)
* [MLflow notes by Jaime Cabrera-Salcedo](https://github.com/jaimeh94/MLOps-Zoomcamp/tree/main/02-experiment-tracking)
* [Experiment tracking with MLflow by Hongfan](https://github.com/Muhongfan/MLops/blob/main/02-experiment-tracking/README.md)
* [Running MLflow with Docker and Minikube](https://open.substack.com/pub/asfandqazi/p/mlflow-on-minikube?r=2o17tf&utm_campaign=post&utm_medium=web)
* [Chapter 2 notes by Marcus](https://github.com/mleiwe/mlops-zoomcamp/blob/Ch2_Marcus/cohorts/2024/02-experiment-tracking/Ch2_notes.md)
* [Experiment tracking by Annaliese Tech](https://github.com/AnnalieseTech/MLOPS_ZOOMCAMP/blob/main/02_EXPERIMENT_TRACKING/EXPERIMENT_TRACKING_NOTES.md)
* [Hyperparameter tuning with MLflow by Annaliese Tech](https://github.com/AnnalieseTech/MLOPS_ZOOMCAMP/blob/main/02_EXPERIMENT_TRACKING/Hyperparameter-Tuning.md)
* [MLflow setup and tracking by Hokfu](https://github.com/Hokfu/MLOps_Zoomcamp_Study/blob/main/02-experiment-tracking/README.md)
* [2025 notes on MLflow and Hyperopt by Gabi Fonseca](https://github.com/fonsecagabriella/ml_ops/blob/main/02_experiment_tracking/__notes.md)
* [Homework 2 article by Srikanth Ganji](https://medium.com/@srikanth.unix07/mlops-zoomcamp-2025-homework-2-experiment-tracking-with-mlflow-4ea1ed783531)
* [Week 2 detailed notes by Muhammad Shifa](https://github.com/MuhammadShifa/mlops-zoomcamp2025/blob/main/02-experiment-tracking/README.md)
* Send a PR, add your notes above this line

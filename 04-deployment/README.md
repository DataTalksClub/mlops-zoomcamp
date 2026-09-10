# Module 4: Model Deployment

We package the duration model as a web service and connect serving to the model registry. We also compare online, streaming, and batch deployment modes.

## 4.1 [Three Ways of Deploying a Model](01-deployment-modes.md)

Compare batch, online, and event-driven streaming deployment and choose the boundary that fits the prediction requirement.

## 4.2 [Web Services: Deploying Models with Flask and Docker](02-flask-docker.md)

Build a Flask prediction endpoint, test it, and package it with its model artifacts in Docker.

## 4.3 [Web Services: Getting Models from the Model Registry](03-model-registry-serving.md)

Load a selected MLflow model version at serving time instead of bundling a fixed artifact into the image.

## 4.4 [Streaming: Deploying Models with Kinesis and Lambda](04-streaming-kinesis-lambda.md)

Optionally consume Kinesis events with a containerized Lambda function and produce predictions.

## 4.5 [Batch: Preparing a Scoring Script](05-batch-scoring.md)

Turn a scoring notebook into a parameterized script that can run scheduled batches and backfills.

## 4.6 [Batch Scoring with Mage](06-mage-batch-scoring.md)

Use a Mage transformation block to retrieve a model from MLflow and apply it to a batch.

## Homework

More information is available in the [Module 4 homework](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/cohorts/2025/04-deployment/homework.md).

## Code and resources

The main code examples are:

- [Flask web service](web-service)
- [MLflow-backed web service](web-service-mlflow)
- [Kinesis and Lambda example](streaming)
- [Batch scoring code](batch)

The streaming exercise can create AWS charges. Treat it as optional and remove test resources when finished. Use the local tests in Module 6 when you don't want to deploy cloud resources.

## Community Notes

Share community notes and resources below.

* [Notes on model deployment and creating a modeling package by Ron M.](https://particle1331.github.io/inefficient-networks/notebooks/mlops/04-deployment/notes.html)
* [Model deployment on Google Cloud Platform by M. Ayoub C.](https://gist.github.com/Qfl3x/de2a9b98a370749a4b17a4c94ef46185)
* [Week 4 deployment notes by Bhagabat](https://github.com/BPrasad123/MLOps_Zoomcamp/tree/main/Week4)
* [Week 4 deployment notes by Ayoub B.](https://github.com/ayoub-berdeddouch/mlops-journey/blob/main/deployment-04.md)
* [Week 4 deployment notes by Waleed](https://github.com/waleedayoub/mlops-zoomcamp/blob/main/cohorts/2023/04-deployment/module4notes.waleed.md)
* [Offline, online, and streaming deployment notes by Hongfan](https://github.com/Muhongfan/MLops/blob/main/04-deployment/README.md)
* [Week 4 notes by Marcus](https://github.com/mleiwe/mlops-zoomcamp/blob/NotesBranch/cohorts/2024/04-deployment/Ch4_Notes_ML.md)
* [2025 model deployment notes by Nitin Gupta](https://github.com/niting9881/course-mlops-zoomcamp/blob/main/04-deployment/README.md)
* [Week 4 detailed notes by Muhammad Shifa](https://github.com/MuhammadShifa/mlops-zoomcamp2025/blob/main/04-deployment/README.md)
* Send a PR, add your notes above this line

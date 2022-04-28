# MLOps Zoomcamp

Our MLOps Zoomcamp course

- Sign up here: https://airtable.com/shrCb8y6eTbPKwSTL (it's not automated, you will not receive an email immediately after filling in the form)
- Register in [DataTalks.Club's Slack](https://datatalks.club/slack.html)
- Join the [`#course-mlops-zoomcamp`](https://app.slack.com/client/T01ATQK62F8/C02R98X7DS9) channel
- [Tweet about the course!](https://ctt.ac/fH67W)


## Overview

### Objective

Teach practical aspects of productionizing ML services — from collecting requirements to model deployment and monitoring.

### Target audience

Data scientists and ML engineers. Also software engineers and data engineers interested in learning about putting ML in production

### Pre-requisites

* Python
* Docker
* Being comfortable with command line 
* Prior exposure to machine learning (at work or from other courses, e.g. from [ML Zoomcamp](https://github.com/alexeygrigorev/mlbookcamp-code/tree/master/course-zoomcamp))
* Prior programming experience (1+ years of professional experience)

### Timeline

Course start: 16 of May



## Syllabus

There are five modules in the course and one project at the end. Each module is 1-2 lessons and homework. One lesson is 60-90 minutes long.

This is a draft and will change. 


### Module 0: Introduction

* What is MLOps
* Running example: NY Taxi trips dataset
* Why do we need MLOps
* Course overview
* Environment preparation


### Module 1: Processes

* CRISP-DM, CRISP-ML
* ML Canvas
* Data Landscape canvas
* (optional) [MLOps Stack Canvas](https://miro.com/miroverse/mlops-stack-canvas/)
* Documentation practices in ML projects (Model Cards Toolkit)

Instructors: Larysa Visengeriyeva

2 hours 


### Module 2: Training

* Tracking experiments
* MLFlow
* Model registry
* ML pipelines, TFX, Kubeflow Pipelines 
* Scheduling pipelines (Airflow?)
* Model testing

Instructors: Cristian Martinez, Theofilos Papapanagiotou 

Homework:

* ? something with MLFlow perhaps as it’s easier to run locally


### Module 3: Serving

* Batch vs online
* For online: web services vs streaming
* Serving models with Kubeflow+Kubernetes (refer to ML Zoomcamp)
* Serving models in Batch mode (AWS Batch, Spark)
* Streaming (Kinesis/SQS + AWS Lambda)

Instructors: Alexey Grigorev

Homework:

* Deploy a model with Spark (local mode) 


### Module 4: Monitoring

* ML monitoring VS software monitoring 
* Data quality monitoring
* Data drift / concept drift 
* Batch VS real-time monitoring 
* Tools: Evidently
* Tools: Prometheus/Grafana

Instructors: Emeli Dral

Homework:

* ?

Other things:

* Data quality issues 
* Alerts


### Module 5: Best practices

* Devops
* Virtual environments and Docker
* Python: logging, linting
* Testing: unit, integration, regression 
* CI/CD (github actions)
* Infrastructure as code (terraform, cloudformation)
* Cookiecutter
* Makefiles

Instructors: Sejal Vaidya

Homework:

* ? 


### Project

* End-to-end project with all the things above


## Running example

To make it easier to connect different modules together, we’d like to use the same running example throughout the course.

Possible candidates: 

* [https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page) - predict the ride duration or if the driver is going to be tipped or not


## Instructors

- Larysa Visengeriyeva
- Cristian Martinez
- Theofilos Papapanagiotou 
- Alexey Grigorev
- Emeli Dral
- Sejal Vaidya

## Other courses from DataTalks.Club:

- [Machine Learning Zoomcamp - free 4-month course about ML Engineering](https://github.com/alexeygrigorev/mlbookcamp-code/tree/master/course-zoomcamp)
- [Data Engineering Zoomcamp - free 9-week course about Data Engineering](https://github.com/DataTalksClub/data-engineering-zoomcamp/)

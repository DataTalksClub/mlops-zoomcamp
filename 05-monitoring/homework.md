## 5.5 Homework

> This homework is prepared by [Nakul Bajaj](https://github.com/Nakulbajaj101). Thank you Nakul!

In this homework, we'll monitor the ride duration model deployed in batch mode. We will use green taxi data for this task. 
Before we start the homework we want to set up few things and make sure data is available.

We have provided with two models:

* one trained on 03-2021
* another trained on both 03-2021 and 04-2021

Both models are linear regression models. If you want to know how they are trained, check [homework/model_training.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/homework/model_training.py). 

Both models will be uploaded in the docker image, we will use `ENVIRONMENT` variables in the docker-compose file, to specify
which one to use. 

There is a `requirements.txt` to setup your conda or virtual environment.
You can create a datasets folder in the `homework` directory or modify location for Q3 to Q7

## Preparation

To download data from 03-2021 to 05-2021, run
[`prepare.py`](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/homework/prepare.py).
If you create the datasets folder, then you don't have to modify this file, 
else modify it to point to the location where you want to store the data. 

If you get 403 errors, change it to S3 location or reach out in the channel,
this issue has been addressed in the slack channel.

For Q6 and Q7 we want to prepare the dataset which combines 03-2021 and Q4-2021.
Run the [`prepare_reference_data.py`](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/homework/prefect-monitoring/prepare_reference_data.py)
script for that.

You'll find all the starter code in the [homework](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/homework/) directory.


## Q1. Docker compose

We'll start with the docker compose file in the homework directory. The file is ready to use and is in 
[homework/docker-compose-homework.yml](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/homework/docker-compose-homework.yml).

Run docker compose. Once up and running, open the localhost for mongo.

What’s the message you get in browser at [http://localhost:27017](http://localhost:27017)?

* No message is displayed (empty)
* It looks like you are trying to access MongoDB over HTTP on the native driver port
* This is a cool prediction service
* None of the above


## Q2. Docker volume

In the docker compose file we have specified the volume. We do it because we don't want to 
lose the data when we restart the services.

We want to know what is this volume, so we can keep it safe and not delete it. 

What is the command to find the name of our volume?

* `docker ls`
* `docker images`
* `docker volume rm`
* `docker volume ls`


## Q3. Sending data to the prediction service

The service is now up and running. When the requet comes in, it makes the prediction,
and then saves it to mongo DB. Inspect the [homework/prediction_service/app.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/homework/prediction_service/app.py) file.
We want to simulate traffic and get it ready for monitoring. For that we have prepared a python script [homework/prefect-monitoring/send_data.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/homework/prefect-monitoring/send_data.py).

Run this script to score 5000 random datapoints for period 2021-05.

What is the last prediction by the current model?

* 22.16
* 15.74 
* 9.93 
* 27.24


## Q4. Generate evidently report using Prefect

We have prepared the prefect monitoring script, which will use the `target.csv`
file prepared in the previous step. In the script we have provided the reference
data file (data on which model was trained on, 03-2021). We want to know if the
trips in 05-2021 deviated from 03-2021.

You may have to modify two functions in the prefect monitoring script to generate
the evidently profile and evidently report, `save_report` and `save_html_report`.

The monitoring script is located in [homework/prefect-monitoring/prefect_monitoring.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/homework/prefect-monitoring/prefect_monitoring.py)

How many model features have drifted based on the html report?

* 3
* 2
* 5
* 0


## Q5. Name of the test 

What’s the stats test for location ids?


## Q6. Sending data to the prediction service with new model

Suppose some of the features have drifted. We want to run the new model
to observe how it performs and compare it to the previous model.
To do this, we need to make few modifications. In the docker compose file, 
change two environment variables: `MODEL_FILE` and `MODEL_VERSION`, pointing
to the other model and providing a new model version.

Once updated, restart the servers, so environment variables are updated.

Similar to Q3, we will simulate the traffic with same data points, running
the `send_data.py` file.

Before we run this, we need to clean the mongo database. 

To do it, run [homework/prefect-monitoring/clean_mongo.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/homework/prefect-monitoring/clean_mongo.py).

What is the last prediction made by the new model?

* 15.74
* 16.64
* 37.002
* 8.50


## Q7. Generate evidently report using Prefect with new model

In this step we want to use the new reference data, which is a combination of 03-2021 and 04-2021. 
This should be the reference dataset because it was used to
train the `lin_reg_V2.bin` model.

Modify lines 22 and 24 in `prefect_monitoring.py` script to point to new 
data file and new model, then run the Prefect script.

Which model feature detected drift when we run with the new model and new reference
dataset, in comaprison to old run?

* DOLocationID
* PULocationID
* target
* trip_distance


## Q8. Bonus Question (Not marked)

Whats the length of the metrics for collection name "report" stored as a collection in mongo db?

Use this jupyter notebook: [homework/prefect-monitoring/monitor_profile.ipynb](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/homework/prefect-monitoring/monitor_profile.ipynb)

* 2
* 9 
* 5
* NA (empty)


## Submit the results

* The homework is optional and there's no form for submitting the results 
* Its possible results may not match, but should be close


## Solution

We'll post the solution here soon




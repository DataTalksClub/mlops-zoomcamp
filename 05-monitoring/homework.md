## 5.5 Homework

In this homework, we'll monitor the ride duration model in batch mode. We will use green taxi data for this task. 
Before we start the homework we want to set up few things and make sure data is available.

We have provided with two models one trained on 03-2021 and another trained on 03-2021 and 04-2021. Both models are linear regression 
models, we have provided the script so you know how these were created. You don't have to run this script, but is provided for your reference [homework/model_training.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/74324e4d3759e9712ce406b8b30c77cff66e6cef/05-monitoring/homework/model_training.py). 
Both models will be uploaded in the docker image, we will use ENVIRONMENT variables in docker compose file, to inform prediction 
service which one to use. 

There is a requirements.txt file provided in the directory to setup your conda or virtual environment.
You want to create a datasets folder in the homework directory or modify location for Q3 to Q7

Run `prepare.py` to download data from 03-2021 to 05-2021. If you create the datasets folder, then you don't have to modify this file, 
else modify it to point to the location where you want to store the data. [homework/prepare.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/74324e4d3759e9712ce406b8b30c77cff66e6cef/05-monitoring/homework/prepare.py). If you get 403 errors, change it to S3 location or reach out in the channel,
this issue has been addressed in the slack channel.

For Q6 and Q7 we want to prepare the dataset which combines 03-2021 and Q4-2021. You want to run the script `prepare_reference_data.py`, to proceed further.
[homework/prefect_monitoring/prepare_reference_data.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/74324e4d3759e9712ce406b8b30c77cff66e6cef/05-monitoring/homework/prefect_monitoring/prepare_reference_data.py)


You'll find all the starter code in the [homework](https://github.com/DataTalksClub/mlops-zoomcamp/blob/74324e4d3759e9712ce406b8b30c77cff66e6cef/05-monitoring/homework/) directory.


## Q1. Docker compose

We'll start with the docker compose file in the homework directory. The file is ready to use and is in 
[homework/docker-compose-homework.yml](https://github.com/DataTalksClub/mlops-zoomcamp/blob/74324e4d3759e9712ce406b8b30c77cff66e6cef/05-monitoring/homework/docker-compose-homework.yml).

Run the docker compose file, once up and running, open the localhost for mongo.

What’s the message we get in browser at url localhost:27017?

* No message is displayed (empty)
* It looks like you are trying to access MongoDB over HTTP on the native driver port
* This is a cool prediction service
* None of the above


## Q2. Docker volume

In the docker compose file we have specified the volume. This is so that we don't lose the data when we restart the service and new container is running.
We want to know what is this volume, so we can keep it safe and not delete it. 

What is the command to find the name of our volume?


* docker ls
* docker images
* docker volume rm
* docker volume ls


## Q3. Sending data to the prediction service

The prediction service is up and running, when the requet comes in, prediction is made, then sent and stored in mongo DB. Inspect the file app.py in location [homework/prediction_service/app.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/74324e4d3759e9712ce406b8b30c77cff66e6cef/05-monitoring/homework/prediction_service/app.py). We want to simulate traffic and get it ready for monitoring. For that we have prepared a python script [homework/prefect_monitoring/send_data.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/74324e4d3759e9712ce406b8b30c77cff66e6cef/05-monitoring/homework/prefect_monitoring/send_data.py). Run this script, 5000 random datapoints for period 2021-05 are scored.

What is the last prediction by the current model?

* 22.16
* 15.74 
* 9.93 
* 27.24


## Q4. Generate evidently report using prefect

We have prepared the prefect monitoring script, which will use the target.csv file prepared in the previous step. In the script we have provided the reference
data file (data on which model was trained on, 03-2021). We want to know if the trips in 05-2021 deviated from 03-2021. You may have to modify two functions in the prefect monitoring script to generate the evidently profile and evidently report, `save_report` and `save_html_report`. The monitoring script is located here. [homework/prefect_monitoring/prefect_monitoring.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/74324e4d3759e9712ce406b8b30c77cff66e6cef/05-monitoring/homework/prefect_monitoring/prefect_monitoring.py)

How many model features have drifted based on the html report?

* 3
* 2
* 5
* 0


## Q5. Name the stats test 

What’s the stats test for location ids?


## Q6. Sending data to the prediction service with new model

Lets say some features have drifted, we want to run the new model to observe how it performs compared to previous model. In order to do this we may have to make few modifications. In the docker compose file, we want to change two environment variables, `MODEL_FILE` and `MODEL_VERSION` pointing to the other model and providing a new model version. Once updated, we want to restart the docker images, so environment variables are updated.
Similat to Q3, we will simulate the traffic with same data points, running `send_data.py` file. Before we run this we want to clean the mongo database, and we want to ensure we are starting clean. This step is just for the homework, in real life, you may have better techniques to manage this. 

The clean db script is located here. [homework/prefect_monitoring/clean_mongo.py](https://github.com/DataTalksClub/mlops-zoomcamp/blob/74324e4d3759e9712ce406b8b30c77cff66e6cef/05-monitoring/homework/prefect_monitoring/clean_mongo.py)


What is the last prediction made by the new model?

* 15.74
* 16.64
* 37.002
* 8.50


## Q7. Generate evidently report using prefect with new model

In this step we want to use the new reference data, which is a combination of 03-2021 and 04-2021, since combination of these data points were used to
train the `lin_reg_V2.bin` model. You may have prepared this data file at the start. Modify lines 22 and 24 in `prefect_monitoring.py` script to point to new 
data file and new model, then run the prefect script.

Which model feature detected drift when we run with the new model and new reference dataset, in comaprison to old run?

* DOLocationID
* PULocationID
* target
* trip_distance


## Q8. Bonus Question (Not marked)

Whats the length of the metrics for collection name "report" stored as a collection in mongo db?
Use the jupyter notebook `monitor_profile.ipynb` located [homework/prefect_monitoring/monitor_profile.ipynb](https://github.com/DataTalksClub/mlops-zoomcamp/blob/74324e4d3759e9712ce406b8b30c77cff66e6cef/05-monitoring/homework/prefect_monitoring/monitor_profile.ipynb)

* 2
* 9 
* 5
* NA (empty)

Now let's put everything into a virtual environment. We'll use pipenv for that.

Install all the required libraries. Pay attention to the Scikit-Learn version:
check the starter notebook for details. 

After installing the libraries, pipenv creates two files: `Pipfile`
and `Pipfile.lock`. The `Pipfile.lock` file keeps the hashes of the
dependencies we use for the virtual env.

What's the first hash for the Scikit-Learn dependency?


## Q5. Parametrize the script

Let's now make the script configurable via CLI. We'll create two 
parameters: year and month.

Run the script for March 2021. 

What's the mean predicted duration? 

* 11.29
* 16.29
* 21.29
* 26.29

Hint: just add a print statement to your script.




## Submit the results

* Submit your results here: TBA
* Its possible results may not match, but should be close

## Deadline

TBA


## Solution

After the deadline, we'll post the solution here

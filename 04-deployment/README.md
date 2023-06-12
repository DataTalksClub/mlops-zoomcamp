# 4. Model Deployment

## 4.1 Three ways of deploying a model

<a href="https://www.youtube.com/watch?v=JMGe4yIoBRA&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-4-01.jpg">
</a>



## 4.2 Web-services: Deploying models with Flask and Docker

<a href="https://www.youtube.com/watch?v=D7wfMAdgdF8&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-4-02.jpg">
</a>


[See code here](web-service/)


## 4.3 Web-services: Getting the models from the model registry (MLflow)

<a href="https://www.youtube.com/watch?v=aewOpHSCkqI&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-4-03.jpg">
</a>


[See code here](web-service-mlflow/)


## 4.4 (Optional) Streaming: Deploying models with Kinesis and Lambda 

<a href="https://www.youtube.com/watch?v=TCqr9HNcrsI&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-4-04.jpg">
</a>


[See code here](streaming/)


## 4.5 Batch: Preparing a scoring script

<a href="https://www.youtube.com/watch?v=18Lbaaeigek&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-4-05.jpg">
</a>


[See code here](batch/)


## 4.6 MLOps Zoomcamp 4.6 - Batch: Scheduling batch scoring jobs with Prefect

**Note:** There are several changes to deployment in Prefect 2.3.1 since 2.0b8:
- `DeploymentSpec` in 2.0b8 now becomes `Deployment`. 
- `work_queue_name` is used instead of `tags` to submit the deployment to the a specific work queue. 
- You don't need to create a work queue before using the work queue. A work queue will be created if it doesn't exist. 
- `flow_location` is replaced with `flow`
- `flow_runner` and `flow_storage` are no longer supported

```python
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule
from score import ride_duration_prediction

deployment = Deployment.build_from_flow(
    flow=ride_duration_prediction,
    name="ride_duration_prediction",
    parameters={
        "taxi_type": "green",
        "run_id": "e1efc53e9bd149078b0c12aeaa6365df",
    },
    schedule=CronSchedule(cron="0 3 2 * *"),
    work_queue_name="ml",
)

deployment.apply()
```

<a href="https://www.youtube.com/watch?v=ekT_JW213Tc&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-4-06.jpg">
</a>

## 4.7 Choosing the right way of deployment

COMING SOON


## 4.8 Homework

More information [here](../cohorts/2023/04-deployment/homework.md).


## Notes

Did you take notes? Add them here:

* [Notes on model deployment (+ creating a modeling package) by Ron M.](https://particle1331.github.io/inefficient-networks/notebooks/mlops/04-deployment/notes.html)
* [Notes on Model Deployment using Google Cloud Platform, by M. Ayoub C.](https://gist.github.com/Qfl3x/de2a9b98a370749a4b17a4c94ef46185)
* [Week4: Notes on Model Deployment by Bhagabat](https://github.com/BPrasad123/MLOps_Zoomcamp/tree/main/Week4)
* [Week 4: Deployment notes by Ayoub.B](https://github.com/ayoub-berdeddouch/mlops-journey/blob/main/deployment-04.md)
* Send a PR, add your notes above this line

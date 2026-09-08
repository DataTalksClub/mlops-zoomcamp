# 5. Model Monitoring

## 5.1 Intro to ML monitoring

<a href="https://www.youtube.com/watch?v=SQ0jBwd_3kk&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/SQ0jBwd_3kk">
</a>

<figure>
  <img src="images/illustrations/05-01-ml-monitoring-loop.png" alt="A deployed model sending data and predictions to monitoring, alerts, investigation, and feedback">
  <figcaption>Monitoring turns production signals into alerts, investigation, and feedback for the next model iteration.</figcaption>
</figure>



## 5.2 Environment setup

<a href="https://www.youtube.com/watch?v=yixA3C1xSxc&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/yixA3C1xSxc">
</a>

<figure>
  <img src="images/illustrations/05-02-monitoring-environment.png" alt="A local monitoring stack connecting a metrics worker, database, dashboard, and terminal">
  <figcaption>A reproducible local stack connects metric calculation, durable storage, and dashboard inspection.</figcaption>
</figure>



## 5.3 Prepare reference and model

<a href="https://www.youtube.com/watch?v=IjNrkqMYQeQ&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/IjNrkqMYQeQ">
</a>

<figure>
  <img src="images/illustrations/05-03-reference-model-preparation.png" alt="Historical data and a training notebook producing a reference dataset and baseline model">
  <figcaption>Monitoring starts with a reference dataset and baseline model that future production batches can be compared against.</figcaption>
</figure>



## 5.4 Evidently metrics calculation

<a href="https://www.youtube.com/watch?v=kP3lzh_HfWY&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/kP3lzh_HfWY">
</a>

<figure>
  <img src="images/illustrations/05-04-evidently-metrics.png" alt="Reference and current datasets compared to produce distribution, gauge, and performance metrics">
  <figcaption>Metrics calculation compares a reference with a current batch and emits drift, quality, and performance signals.</figcaption>
</figure>


## 5.5 Evidently Monitoring Dashboard

<a href="https://www.youtube.com/watch?v=zjvYhDPzFlY&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/zjvYhDPzFlY">
</a>

<figure>
  <img src="images/illustrations/05-05-monitoring-dashboard.png" alt="A monitoring dashboard showing trends, a gauge, distribution comparison, and alert status from stored metrics">
  <figcaption>A dashboard turns stored monitoring metrics into trends, comparisons, and actionable status signals.</figcaption>
</figure>


## 5.6 Dummy monitoring

<a href="https://www.youtube.com/watch?v=s3G4PMsOMOA&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/s3G4PMsOMOA">
</a>

<figure>
  <img src="images/illustrations/05-06-dummy-monitoring.png" alt="Synthetic batches repeating through a monitoring test harness, metric store, and checked dashboard signal">
  <figcaption>Dummy monitoring safely exercises the metric pipeline with repeatable synthetic batches.</figcaption>
</figure>



## 5.7 Data quality monitoring

<a href="https://www.youtube.com/watch?v=fytrmPbcLhI&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/fytrmPbcLhI">
</a>

> Note: in this video we use Prefect (07:33-11:21). Feel free to skip this part. Also note that Prefect
is not officially supported in the 2024 edition of the course.


## 5.8 Save Grafana Dashboard

<a href="https://www.youtube.com/watch?v=-c4iumyZMyw&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/-c4iumyZMyw">
</a>



## 5.9 Debugging with test suites and reports

<a href="https://www.youtube.com/watch?v=sNSk3ojISh8&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/sNSk3ojISh8">
</a>


## Homework


More information [here](../cohorts/2025/05-monitoring/homework.md)


## Notes

Did you take notes? Add them here:

* [Week 5 notes by M. Ayoub C.](https://gist.github.com/Qfl3x/aa6b1bec35fb645ded0371c46e8aafd1)
* [week 5: Monitoring notes Ayoub.B](https://github.com/ayoub-berdeddouch/mlops-journey/blob/main/monitoring-05.md)
* [Week 5: 2023](https://github.com/dimzachar/mlops-zoomcamp/tree/master/notes/Week_5)
* [Week5: Why we need to monitor models after deployment? by Hongfan (Amber)](https://github.com/Muhongfan/MLops/blob/main/05-monitoring/README.md)
* [week-5: Detailed Notes about Monitoring, codes and homework by Muhammad Shifa](https://github.com/MuhammadShifa/mlops-zoomcamp2025/blob/main/05-monitoring/README.md)
* Send a PR, add your notes above this line



# Monitoring example

## Notes
There were a massive update for Evidently since 0.7.0 version.

To check working example with Evidently >= 0.7.0 go to `post-evidently-0.7` folder.

## Prerequisites

You need following tools installed:
- `docker`
- `docker-compose` (included to Docker Desktop for Mac and Docker Desktop for Windows )

## Preparation

Note: all actions expected to be executed in repo folder.

- Create virtual environment and activate it (eg. `python -m venv venv && source ./venv/bin/activate` or `conda create -n venv python=3.11 && conda activate venv`)
- Install required packages `pip install -r requirements.txt`
- Run `baseline_model_nyc_taxi_data.ipynb` for downloading datasets, training model and creating reference dataset 

## Monitoring Example

### Starting services

To start all required services, execute:
```bash
docker-compose up
```

It will start following services:
- `db` - PostgreSQL, for storing metrics data
- `adminer` - database management tool
- `grafana` - Visual dashboarding tool 


### Sending data

To calculate evidently metrics with prefect and send them to database, execute:
```bash
python evidently_metrics_calculation.py
```

This script will simulate batch monitoring. Every 10 seconds it will collect data for a daily batch, calculate metrics and insert them into database. This metrics will be available in Grafana in preconfigured dashboard. 

### Accsess dashboard

- In your browser go to a `localhost:3000`
The default username and password are `admin`

- Then navigate to `General/Home` menu and click on `Home`.

- In the folder `General` you will see `New Dashboard`. Click on it to access preconfigured dashboard.

### Ad-hoc debugging

Run `debugging_nyc_taxi_data.ipynb` to see how you can perform a debugging with help of Evidently `TestSuites` and `Reports`

### Stopping services

To stop all services, execute:
```bash
docker-compose down
```

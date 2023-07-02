# 5. Model Monitoring

## 5.1 Monitoring for ML-based services

<a href="https://www.youtube.com/watch?v=gMiT11Bp05A&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-5-01.jpg">
</a>


[Slides](https://drive.google.com/file/d/1wcMU75ZcNNJie4ELjsKPkITIL93wHykt/view?usp=sharing)


## 5.2 Setting up the environment

<a href="https://www.youtube.com/watch?v=VkkpVXW53bo&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-5-02.jpg">
</a>



## 5.3 Creating a prediction service and simulating traffic

<a href="https://www.youtube.com/watch?v=umQ3Mo5G1o8&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-5-03.jpg">
</a>



## 5.4 Realtime monitoring walktrough (Prometheus, Evidently, Grafana)

<a href="https://www.youtube.com/watch?v=r_m4VFEJ8yY&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-5-04.jpg">
</a>



## 5.5 Batch monitoring walktrough (Prefect, MongoDB, Evidently)

<a href="https://www.youtube.com/watch?v=KefdYuue_FE&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-5-05.jpg">
</a>



## 5.6 Homework

More information here: TBD


## Notes

Did you take notes? Add them here:

* [Week 5 notes by M. Ayoub C.](https://gist.github.com/Qfl3x/aa6b1bec35fb645ded0371c46e8aafd1)
* [week 5: Monitoring notes Ayoub.B](https://github.com/ayoub-berdeddouch/mlops-journey/blob/main/monitoring-05.md)
* Send a PR, add your notes above this line



# Monitoring example

## Prerequisites

You need following tools installed:
- `docker`
- `docker-compose` (included to Docker Desktop for Mac and Docker Desktop for Windows )

## Preparation

Note: all actions expected to be executed in repo folder.

- Create virtual environment and activate it (eg. `python -m venv venv && source ./venv/bin/activate`)
- Install required packages `pip install -r requirements.txt`
- Run `python prepare.py` for downloading datasets

## Monitoring Example

### Starting services

To start all required services, execute:
```bash
docker-compose up
```

It will start following services:
- `prometheus` - TSDB for metrics
- `grafana` - Visual tool for metrics
- `mongo` - MongoDB, for storing raw data, predictions, targets and profile reports
- `evidently_service` - Evindently RT-monitoring service (draft example)
- `prediction_service` - main service, which makes predictions

### Sending data

To start sending data to service, execute:
```bash
python send_data.py
```

This script will send every second single row from dataset to prediction service along with creating file `target.csv` with actual results (so it can be loaded after)

## Batch Monitoring Example

After you stop sending data to service, you can run batch monitoring pipeline (using Prefect) by running script:

```bash
python prefect_example.py
```

This script will:
- load `target.csv` to MongoDB
- download dataset from MongoDB
- Run Evidently Model Profile and Evidently Report on this data
- Save Profile data back to MongoDB
- Save Report to `evidently_report_example.html`

You can look at Prefect steps in Prefect Orion UI
(to start it execute `prefect orion start`)

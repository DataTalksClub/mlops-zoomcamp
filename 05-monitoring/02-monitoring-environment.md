---
video_url: "https://www.youtube.com/watch?v=yixA3C1xSxc&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
code:
  - label: "Monitoring Compose stack"
    path: docker-compose.yml
  - label: "Monitoring requirements"
    path: requirements.txt
---

# Environment Setup

The monitoring example uses a small local stack. Python calculates metrics, PostgreSQL stores them, and Grafana displays them. Adminer is useful for inspecting the database while developing.

## Create the Python environment

Create a dedicated environment for the monitoring code and install the packages in `requirements.txt`. The current requirements set Evidently to 0.6.7. We keep the newer API example in `post-evidently-0.7`.

![The monitoring project files and Python setup](images/02-monitoring-environment-01-compose.jpg)

Store the reference data alongside the model under the local `data/` and `models/` directories. The repository ignores their generated contents, so each learner can create them locally.

## Start the services

The Compose file defines the database, Adminer, and Grafana. Use volumes for database state and mount Grafana configuration so the data source survives a container restart.

![PostgreSQL and Grafana services in Docker Compose](images/02-monitoring-environment-02-services.jpg)

Run `docker-compose up` to start the stack, then open Grafana at `http://localhost:3000`. The example uses `admin` and `admin` as default credentials, while Adminer provides a separate browser interface for checking the PostgreSQL tables.

![The local monitoring dashboard](images/02-monitoring-environment-03-dashboard.jpg)

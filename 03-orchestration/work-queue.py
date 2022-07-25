from prefect import flow

@flow
def myflow():
    print("hello")

from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import IntervalSchedule
from prefect.flow_runners import SubprocessFlowRunner
from datetime import timedelta

Deployment(
    flow=myflow,
    name="model_training-dev",
    schedule=IntervalSchedule(interval=timedelta(minutes=5)),
    flow_runner=SubprocessFlowRunner(),
    tags=["dev"]
)

Deployment(
    flow=myflow,
    name="model_training-prod",
    schedule=IntervalSchedule(interval=timedelta(minutes=5)),
    flow_runner=SubprocessFlowRunner(),
    tags=["prod"]
)


from prefect import flow

@flow
def myflow():
    print("hello")

from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import IntervalSchedule
from datetime import timedelta

deployment_dev = Deployment.build_from_flow(
    flow=myflow,
    name="model_training-dev",
    schedule=IntervalSchedule(interval=timedelta(minutes=5)),
    work_queue_name="dev"
)

deployment_dev.apply()

deployment_prod = Deployment.build_from_flow(
    flow=myflow,
    name="model_training-prod",
    schedule=IntervalSchedule(interval=timedelta(minutes=5)),
    work_queue_name="prod"
)

deployment_prod.apply()


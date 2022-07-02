from prefect.deployments import DeploymentSpec
from prefect.orion.schemas.schedules import CronSchedule
from prefect.flow_runners import SubprocessFlowRunner

DeploymentSpec(
    flow_location="score.py",
    name="ride_duration_prediction",
    parameters={
        "run_id": "20c7e3f3b3584b769bf6cacd4643d43d"
    },
    flow_storage="74833080-d772-4b2f-8c03-b08fb6dbc70c",
    schedule=CronSchedule(cron="0 3 2 * *"),
    flow_runner=SubprocessFlowRunner(),
    tags=["ml","ride_prediction"]
)
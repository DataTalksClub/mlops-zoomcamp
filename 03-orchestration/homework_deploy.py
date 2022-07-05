from prefect.deployments import DeploymentSpec
from prefect.orion.schemas.schedules import CronSchedule
from prefect.flow_runners import SubprocessFlowRunner

DeploymentSpec(
    name="scheduled-deployment",
    flow_location="homework.py",
    schedule=CronSchedule(cron="0 9 15 * *"),
    flow_runner = SubprocessFlowRunner()
)




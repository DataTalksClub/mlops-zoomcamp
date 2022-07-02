from datetime import datetime

from dateutil.relativedelta import relativedelta
from prefect import flow
from prefect.task_runners import SequentialTaskRunner

from score import batch_score


@flow(name="backfill_scoring", task_runner=SequentialTaskRunner())
def backfill_runs():

    start_date = datetime(year=2021, month=3, day=1)
    end_date = datetime(year=2022, month=5, day=1)

    d = start_date

    while d <= end_date:
        batch_score(date=d, 
                    run_id='20c7e3f3b3584b769bf6cacd4643d43d')

        d = d + relativedelta(months=1)

if __name__ == "__main__":
    backfill_runs()


import homework

from typing import List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from prefect import task, flow, get_run_logger


@flow
def backfill(dates: List[str] = None):
    for date in dates: 
        homework.main(date)


def run():
    start = datetime(year=2021, month=1, day=1)
    end = datetime(year=2022, month=1, day=1)

    dates = []

    d = start
    while d <= end: 
        dates.append(d.strftime('%Y-%m-%d'))
        d = d + relativedelta(months=1)

    print(dates)
    backfill(dates)


if __name__ == '__main__':
    run()
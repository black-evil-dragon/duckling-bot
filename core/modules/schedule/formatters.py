from datetime import datetime, timedelta
from typing import Dict, List


def get_date_by_weekday(start_date, weekday):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    delta = (weekday - 1) - start.weekday()

    if delta < 0:
        delta += 7

    target_date = start + timedelta(days=delta)

    return target_date.strftime("%d.%m.%Y")


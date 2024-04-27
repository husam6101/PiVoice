from pi_voice.operators.DataOperator import DataOperator
from pi_voice.config import config, get_path_from

import datetime
import time
import asyncio


# Time of Day and Day of Week
def get_time_of_day_and_day_of_week():
    current_date = datetime.datetime.now()
    day_of_week = current_date.strftime("%a")
    time_of_day = current_date.strftime("%H:%M")
    return time_of_day, day_of_week


def get_next_notable_timestamp():
    data_op = DataOperator()

    return data_op.get_next_notable_timestamp(
        data_op.extract_time_ranges(
            data_op.load_csv(get_path_from(config["lgbm"]["dataset"]))
        )
    )

def retry_on_exception(func, *args, **kwargs):
    max_retries = 3
    delay = 0.1
    
    for i in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(delay)
            else:
                raise e

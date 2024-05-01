import pandas as pd
import csv
import pickle
from pi_voice import logger
from datetime import datetime


class DataOperator:
    def __init__(self):
        pass

    def load_csv(self, filepath):
        return pd.read_csv(filepath)

    def add_row_to_csv(self, filepath, row_data):
        with open(filepath, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row_data)

    def save_label_encoder(self, label_encoder, path):
        with open(path, "wb") as file:
            pickle.dump(label_encoder, file)

    def load_label_encoder(self, path):
        with open(path, "rb") as file:
            return pickle.load(file)

    def extract_time_ranges(
        self,
        data,
        time_column="time_of_day",
        action_column="commands",
        ignore_actions=["do_nothing"],
        time_threshold=600,
    ):
        data[time_column] = pd.to_datetime(data[time_column], format="%H:%M").dt.time
        logger.debug("Data loaded and converted successfully.")

        data.sort_values(by=time_column, inplace=True)

        time_ranges = []
        start_time = None

        for row in data.itertuples(index=False):
            if getattr(row, action_column) in ignore_actions:
                continue

            if start_time is None:
                start_time = getattr(row, time_column)
            else:
                if (
                    self._get_time_diff(getattr(row, time_column), start_time)
                    >= time_threshold
                ):
                    time_ranges.append((start_time, getattr(row, time_column)))
                    start_time = getattr(row, time_column)
        return time_ranges

    def _get_time_diff(self, t1, t2, in_seconds=True):
        diff = datetime.combine(datetime.now().date(), t1) - datetime.combine(
            datetime.now().date(), t2
        )

        return diff.total_seconds() if in_seconds else diff

    def _add_time_diff(self, t, diff):
        return (datetime.combine(datetime.now().date(), t) + diff).time()

    def get_next_notable_timestamp(self, time_ranges):
        now = datetime.now().time()
        logger.debug(f"Current time: {now}")
        # Collect all notable times based on the 'only_start' parameter
        notable_times = []
        for start, end in time_ranges:
            notable_times.append(start)
        logger.debug(f"{len(notable_times)} notable times found.")

        # Filter times that are in the future relative to 'now'
        future_times = [t for t in notable_times if t > now]
        # if there are no future times, use the first notable (earliest)
        if len(future_times) == 0:
            future_times = [notable_times[0]]

        # Return the closest future time if available,
        # else return None if there are no future times
        if future_times:
            logger.debug(f"Closest future time: {min(future_times)}")
            return min(future_times)
        else:
            return None

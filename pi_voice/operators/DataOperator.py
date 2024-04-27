import pandas as pd
import csv
import pickle
from datetime import datetime, time
from pi_voice import logger


class DataOperator:
    def __init__(self):
        pass

    def load_csv(self, filepath):
        return pd.read_csv(filepath)

    def add_row_to_csv(self, filepath, row_data):
        with open(filepath, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row_data)
        print("Row added successfully to:", filepath)

    def save_label_encoder(self, label_encoder, path):
        with open(path, 'wb') as file:
            pickle.dump(label_encoder, file)

    def load_label_encoder(self, path):
        with open(path, 'rb') as file:
            return pickle.load(file)

    def extract_time_ranges(
            self,
            data,
            time_column="time_of_day",
            command_column="commands",
            ignore_commands=[],
            time_threshold=600,
    ):
        data[time_column] = pd.to_datetime(data[time_column])

        # Group the data by commands
        grouped_data = data.groupby(command_column)

        time_ranges = []

        # Iterate over each group
        for command, group in grouped_data:
            if (command in ignore_commands):
                continue

            # Sort the group by time column
            group = group.sort_values(time_column)

            # Initialize variables for time range extraction
            start_time = None
            end_time = None

            # Iterate over each row in the group
            for row in group.itertuples(index=False):
                # Check if the start time is not set
                if start_time is None:
                    start_time = row.time_of_day
                    end_time = row.time_of_day
                else:
                    # Check if the time difference is greater than
                    # or equal to the threshold
                    if (row.time_of_day - end_time).seconds >= time_threshold:
                        time_ranges.append(
                            (start_time.time(), end_time.time())
                        )

                        # Update the start time and end time
                        start_time = row.time_of_day
                        end_time = row.time_of_day
                    else:
                        # Update the end time
                        end_time = row.time_of_day
        return time_ranges

    def get_next_notable_timestamp(self, time_ranges):
        now = datetime.now().time()

        # Collect all notable times based on the 'only_start' parameter
        notable_times = []
        for start, end in time_ranges:
            notable_times.append(start)

        # Filter times that are in the future relative to 'now'
        future_times = [t for t in notable_times if t > now]

        # Return the closest future time if available,
        # else return None if there are no future times
        if future_times:
            return min(future_times)
        else:
            return None

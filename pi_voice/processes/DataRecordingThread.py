from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Event
from queue import Queue

from pi_voice.config import config, get_path_from
from pi_voice import logger
from pi_voice.operators.DataOperator import DataOperator
from pi_voice.processes.ErrorHandling import ErrorSeverity
from pi_voice.switcher.SensorSwitcher import SensorSwitcher
from pi_voice.utils.common import get_time_of_day_and_day_of_week, retry_on_exception
from pi_voice.utils.synchronization import writing_lgbm_data
from pi_voice import logger


class DataRecordingThread:
    def __init__(
        self,
        sensor_switcher: SensorSwitcher,
        data_queue: Queue,
        error_queue: Queue,
        stop_flag: Event,
        active_processes_count: Synchronized,
    ):
        self.data_op: DataOperator = DataOperator()
        self.sensor_switcher: SensorSwitcher = sensor_switcher
        self.data_queue: Queue = data_queue
        self.error_queue: Queue = error_queue
        self.stop_flag: Event = stop_flag
        self.active_processes_count: Synchronized = active_processes_count

    def run(self):
        self.active_processes_count.value += 1

        while True:
            try:
                action = self.data_queue.get(block=True, timeout=4)
                logger.info("Received action. Fetching data...")
                
                data = self._get_data(action)
                logger.info("Data fetched. Writing data to file...")

                self._write_data_to_file(data)
                logger.info("Done writing data to file.")
            except Exception as e:
                self.error_queue.put((str(e), "io_errors", ErrorSeverity.LOW))
                continue

            if self.stop_flag.is_set():
                self.active_processes_count.value -= 1
                break

    def _get_data(self, action):
        try:
            logger.debug("Fetching data from sensors...")
            temp, humid, light = retry_on_exception(self.sensor_switcher.get_data)
            time_of_day, day_of_week = get_time_of_day_and_day_of_week()
            logger.debug("Done fetching data.")
            
            data = [temp, humid, light, time_of_day, day_of_week, action]
            logger.debug(
                "Data to be written to file: "
                + str(data)
            )
            
            return data
        except Exception as e:
            self.error_queue.put((str(e), "device_errors", ErrorSeverity.HIGH))

    def _write_data_to_file(self, data):
        try:
            logger.debug("Securing thread and writing data file...")
            writing_lgbm_data.acquire(timeout=2.0)
            retry_on_exception(
                self.data_op.add_row_to_csv,
                (
                    get_path_from(config["lgbm"]["dataset"]),
                    data,
                ),
            )
            writing_lgbm_data.release()
            logger.debug("Done writing data file.")
        except Exception as e:
            self.error_queue.put((str(e), "io_errors", ErrorSeverity.HIGH))
            

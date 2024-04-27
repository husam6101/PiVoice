from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Event
from queue import Queue

from pi_voice.config import config, get_path_from
from pi_voice.operators import logger
from pi_voice.operators.DataOperator import DataOperator
from pi_voice.processes.ErrorHandling import ErrorSeverity
from pi_voice.switcher.SensorSwitcher import SensorSwitcher
from pi_voice.utils.common import get_ToD_and_DoW, retry_on_exception
from pi_voice.utils.synchronization import writing_lgbm_data

import time


class DataRecordingThread:
    def __init__(
        self,
        sensor_switcher: SensorSwitcher,
        gpt2_pipe,
        action_prediction_finished_event: Event,
        error_queue: Queue,
        stop_flag: Event,
        active_processes_count: Synchronized,
    ):
        self.data_op: DataOperator = DataOperator()
        self.sensor_switcher: SensorSwitcher = sensor_switcher
        self.gpt2_pipe = gpt2_pipe
        self.action_prediction_finished_event: Event = action_prediction_finished_event
        self.error_queue: Queue = error_queue
        self.stop_flag: Event = stop_flag
        self.active_processes_count: Synchronized = active_processes_count

    def get_data(self, action):
        try:
            logger.info("Fetching data from sensors...")
            temp, humid, light = retry_on_exception(self.sensor_switcher.get_data)
            time_of_day, day_of_week = get_ToD_and_DoW()
            logger.info("Done.")
            logger.info(
                "Data to be written to file: "
                + str([temp, humid, light, time_of_day, day_of_week, action])
            )
            return [temp, humid, light, time_of_day, day_of_week, action]
        except Exception as e:
            self.error_queue.put((str(e), "device_errors", ErrorSeverity.HIGH))

    def run(self, action):
        self.active_processes_count.value += 1

        while True:
            if self.action_prediction_finished_event.wait(timeout=4):
                try:
                    self.gpt2_pipe.recv()
                    
                    data = self._get_data(action)

# continue unencapsulating exceptions
                    try:
                        logger.info("Writing data file...")
                        writing_lgbm_data.acquire(timeout=2.0)
                        retry_on_exception(
                            self.data_op.add_row_to_csv,
                            (
                                get_path_from(config["lgbm"]["dataset"]),
                                data,
                            ),
                        )
                        writing_lgbm_data.release()
                        logger.info("Done.")
                    except Exception as e:
                        self.error_queue.put((str(e), "io_errors", ErrorSeverity.HIGH))
                        continue

                except Exception as e:
                    self.error_queue.put((str(e), "process_errors", ErrorSeverity.LOW))
                    continue
                finally:
                    self.action_prediction_finished_event.clear()

                if self.stop_flag.is_set():
                    self.active_processes_count.value -= 1
                    break
            elif self.stop_flag.is_set():
                self.active_processes_count.value -= 1
                break

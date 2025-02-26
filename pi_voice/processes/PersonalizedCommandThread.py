import time
from multiprocessing.synchronize import Event
from multiprocessing.sharedctypes import Synchronized
from queue import Queue
from pi_voice import logger
from pi_voice.operators.LGBMOperator import LGBMOperator
from pi_voice.processes.ErrorHandling import ErrorSeverity
from pi_voice.switcher.SensorSwitcher import SensorSwitcher
from pi_voice.switcher.ActionSwitcher import ActionSwitcher
from pi_voice.utils.synchronization import writing_lgbm_data
from pi_voice.operators.DataOperator import DataOperator
from datetime import datetime
import pandas as pd

from pi_voice.utils.common import (
    get_next_notable_timestamp,
    get_time_of_day_and_day_of_week,
    retry_on_exception,
)


class PersonalizedCommandThread:
    def __init__(
        self,
        sensor_switcher: SensorSwitcher,
        action_switcher: ActionSwitcher,
        error_queue: Queue,
        stop_flag: Event,
        active_processes_count: Synchronized,
    ) -> None:
        self.data_op = DataOperator()
        self.lgbm: LGBMOperator = LGBMOperator()
        self.sensor_switcher: SensorSwitcher = sensor_switcher
        self.action_switcher: ActionSwitcher = action_switcher
        self.error_queue: Queue = error_queue
        self.stop_flag: Event = stop_flag
        self.active_processes_count: Synchronized = active_processes_count

    def run(self):
        self.active_processes_count.value += 1

        while True:
            if self.stop_flag.is_set():
                self.active_processes_count.value -= 1
                break
            try:
                target_time = None
                try:
                    writing_lgbm_data.acquire(timeout=2.0)
                    logger.info("Getting next target time...")
                    target_time = retry_on_exception(get_next_notable_timestamp, (self.data_op,))
                    writing_lgbm_data.release()
                    logger.info("Done. Target time is " + str(target_time))
                except Exception as e:
                    self.error_queue.put((str(e), "io_errors", ErrorSeverity.HIGH))
                    continue

                if target_time is None:
                    logger.info("Skipping...")
                    continue

                logger.info("Calculating remaining time...")
                remaining_time = self.data_op._get_time_diff(target_time, datetime.now().time())
                logger.info("Done. Remaining time is " + str(remaining_time))

                if target_time is None:
                    logger.info("Skipping...")
                    continue

                if remaining_time > 0:
                    logger.info(f"Waiting for {str(remaining_time)}s")
                    time.sleep(remaining_time)

                prediction = self._predict_with_lgbm()
                if prediction is None:
                    continue

                try:
                    logger.info("Activating action...")
                    retry_on_exception(self.action_switcher.take_action, (prediction,))
                    logger.info("Done.")
                except Exception as e:
                    self.error_queue.put((str(e), "device_errors", ErrorSeverity.HIGH))
                    continue
            except Exception as e:
                self.error_queue.put((str(e), "process_errors", ErrorSeverity.LOW))
            finally:
                time.sleep(61)

    def _predict_with_lgbm(self):
        try:
            logger.info("Training model...")
            self.lgbm.load_data_and_train_model()
            logger.info("Finished training model.")
        except Exception as e:
            self.error_queue.put((str(e), "model_errors", ErrorSeverity.CRITICAL))
            return None

        data_point = None
        try:
            logger.info("Getting data...")
            temp, humid, light = retry_on_exception(self.sensor_switcher.get_data)
            time_of_day, day_of_week = get_time_of_day_and_day_of_week()
            data_point = {
                "humidity": humid,
                "temperature": temp,
                "light_levels": light,
                "time_of_day": time_of_day,
                "day_of_week": day_of_week,
            }
            logger.info("Done.")
        except Exception as e:
            self.error_queue.put((str(e), "device_errors", ErrorSeverity.HIGH))
            return None

        try:
            logger.info("Predicting with LightGBM...")
            prediction = self.lgbm.predict(data_point)
            logger.info("Done. Prediction: " + prediction)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            self.error_queue.put((str(e), "model_errors", ErrorSeverity.CRITICAL))
            return None

        return prediction

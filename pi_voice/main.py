from pi_voice.config import config, get_path_from
from pi_voice.utils.synchronization import writing_lgbm_data
from pi_voice.operators.AudioOperator import AudioOperator
from pi_voice.operators.WhisperOperator import WhisperOperator
from pi_voice.operators.GPTOperator import GPTOperator
from pi_voice.operators.DataOperator import DataOperator
from pi_voice.operators.LGBMOperator import LGBMOperator
from pi_voice.switcher.ActionSwitcher import ActionSwitcher
from pi_voice.switcher.SensorSwitcher import SensorSwitcher
from pi_voice.operators import logger

import threading
import datetime
import time
import signal


class MainProcess:
    def __init__(self):
        self.audio_op = AudioOperator()
        self.whisper = WhisperOperator()
        self.gpt2 = GPTOperator()
        self.action_switcher = ActionSwitcher()
        self.sensor_switcher = SensorSwitcher()
        self.data_op = DataOperator()
        self.lgbm = LGBMOperator()

    def record_audio(self):
        logger.info("Recording audio...")
        recorded_file = self.audio_op.record_audio()
        return recorded_file

    # BEING SENT AUDIO BIT SEQUENCE, MUST CONVERT TO FILE FIRST
    def transcription_command_thread(self, audio):
        thread = threading.Thread(
            target=self._transcription_command_process,
            args=(audio,)
        )
        # thread.daemon = True
        return thread

    def _transcription_command_process(self, audio):
        # 1. process audio into transcript
        logger.info("Transcribing audio...")
        transcript = self.whisper.process(audio)
        logger.info("Done, transcription: " + transcript)

        # 2. process transcript into command
        logger.info("Predicing action...")
        command = self.gpt2.predict(transcript)
        logger.info("Done, predicted command: " + command)

        # 3. activate command
        logger.info("Activating command: " + command)
        self.action_switcher.take_action(command)
        logger.info("Command activated.")

        # 4. get data from sensors and timestamps
        logger.info("Fetching data from sensors...")
        temp, humid, light = self.sensor_switcher.get_data()
        time_of_day, day_of_week = self._get_ToD_and_DoW()
        logger.info("Done.")

        logger.info("Data to be written to file:")
        logger.info([humid, temp, light, command, time_of_day, day_of_week])

        # 5. save command in dataset for lgbm
        logger.info("Writing data file...")
        writing_lgbm_data.acquire()
        self.data_op.add_row_to_csv(
            get_path_from(config["lgbm"]["dataset"]),
            [temp, humid, light, time_of_day, day_of_week, command]
        )
        writing_lgbm_data.release()
        logger.info("Done.")

        logger.info("Waiting for thread break...")
        time.sleep(0.1)  # giving thread breaks
        logger.info("Thread break ended.")

    def _get_ToD_and_DoW(self):  # Time of Day and Day of Week
        current_date = datetime.datetime.now()
        day_of_week = current_date.strftime("%a")
        time_of_day = current_date.strftime("%H:%M")
        return time_of_day, day_of_week

    def personalized_command_thread(self):
        thread = threading.Thread(
            target=self._personalized_command_process
        )
        # thread.daemon = True
        return thread

    def _personalized_command_process(self):
        logger.info("Entered personalized-command process.")
        while True:
            writing_lgbm_data.acquire()
            logger.info("Getting next target time...")
            target_time = self._get_next_notable_timestamp()
            writing_lgbm_data.release()
            logger.info("Done. Target time is " + str(target_time))

            if target_time is None:
                logger.info("Skipping...")
                continue

            logger.info("Calculating remaining time...")
            current_time = time.time()
            remaining_time = target_time - current_time
            logger.info("Done. Remaining time is " + str(remaining_time))

            if target_time is None:
                logger.info("Skipping...")
                continue

            if remaining_time > 0:
                logger.info("Waiting for " + str(remaining_time))
                time.sleep(remaining_time)

            logger.info("Training model...")
            self.lgbm.load_data_and_train_model()
            logger.info("Finished training model.")
            logger.info("Getting data...")
            temp, humid, light = self.sensor_switcher.get_data()
            time_of_day, day_of_week = self._get_ToD_and_DoW()
            data_point = {
                'Humidity (%)': humid,
                'Temperature (C)': temp,
                'Light Levels (lux)': 0,
                'Time of Day': time_of_day,
                'Day of Week': day_of_week
            }
            logger.info("Done.")
            logger.info("Predicting with LightGBM...")
            prediction = self.lgbm.predict(data_point)
            logger.info("Done. Prediction: " + prediction)
            logger.info("Activating action...")
            self.action_switcher.take_action(prediction)
            logger.info("Done.")
            time.sleep(61)

    def _get_next_notable_timestamp(self):
        return self.data_op.get_next_notable_timestamp(
            self.data_op.extract_time_ranges(
                self.data_op.load_csv(
                    get_path_from(config["lgbm"]["dataset"])
                )
            )
        )

    def main_thread(self):
        thread = threading.Thread(
            target=self._run_main_process
        )
        # thread.daemon = True
        return thread

    def _run_main_process(self):
        while True:
            audio = self.record_audio()

            if audio:
                process = self.transcription_command_thread(audio)
                process.start()


def run():
    process = MainProcess()
    action_switcher = ActionSwitcher()
    action_switcher.is_ready_device.on()
    try:
        process.main_thread().start()
        # process.personalized_command_thread().start()
        signal.signal(
            signal.SIGINT,
            lambda signum,
            frame: action_switcher.reset_all()
        )
    except Exception:
        action_switcher.reset_all()


run()

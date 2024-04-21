from pi_voice.config import config, get_path_from
from pi_voice.utils.synchronization import writing_lgbm_data
from pi_voice.operators.AudioOperator import AudioOperator
from pi_voice.operators.WhisperOperator import WhisperOperator
from pi_voice.operators.GPTOperator import GPTOperator
from pi_voice.operators.DataOperator import DataOperator
from pi_voice.operators.LGBMOperator import LGBMOperator
from pi_voice.switcher.ActionSwitcher import ActionSwitcher
from pi_voice.switcher.SensorSwitcher import SensorSwitcher

import threading
import datetime
import time


class MainProcess:
    def __init__(self):
        self.audio_op = AudioOperator()
        self.whisper = WhisperOperator()
        self.gpt = GPTOperator()
        self.action_switcher = ActionSwitcher()
        self.sensor_switcher = SensorSwitcher()
        self.data_op = DataOperator()
        self.lgbm = LGBMOperator()

    def record_audio(self):
        recorded_file = self.audio_op.record_audio()
        return recorded_file

    # BEING SENT AUDIO BIT SEQUENCE, MUST CONVERT TO FILE FIRST
    def transcription_command_thread(self, audio):
        thread = threading.Thread(
            target=self._transcription_command_process,
            args=(audio,)
        )
        thread.daemon = True
        return thread

    def _transcription_command_process(self, audio):
        # 1. process audio into transcript
        transcript = self.whisper.process(audio)

        # 2. process transcript into command
        command = self.gpt.random_command(transcript)

        # 3. activate command
        self.action_switcher.activate(command)

        # 4. get data from sensors and timestamps
        temp, humid, light = self.sensor_switcher.get_data()
        time_of_day, day_of_week = self._get_ToD_and_DoW()

        # 5. save command in dataset for lgbm
        writing_lgbm_data.acquire()
        self.data_op.add_row_to_csv(
            [temp, humid, light, time_of_day, day_of_week, command]
        )
        writing_lgbm_data.release()

        time.sleep(0.1)  # giving thread breaks

    def _get_ToD_and_DoW():  # Time of Day and Day of Week
        current_date = datetime.datetime.now()
        day_of_week = current_date.strftime("%a")
        time_of_day = current_date.strftime("%H:%M")
        return time_of_day, day_of_week

    def personalized_command_thread(self):
        thread = threading.Thread(
            target=self._personalized_command_process
        )
        thread.daemon = True
        return thread

    def _personalized_command_process(self):
        while True:
            writing_lgbm_data.acquire()
            target_time = self._get_next_notable_timestamp()
            writing_lgbm_data.release()

            if target_time is None:
                continue

            current_time = time.time()
            remaining_time = target_time - current_time

            if target_time is None:
                continue

            if remaining_time > 0:
                time.sleep(remaining_time)

            self.lgbm.load_data_and_train_model()
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
        thread.daemon = True
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
        process.personalized_command_thread().start()
    except Exception:
        action_switcher.reset_all()


run()

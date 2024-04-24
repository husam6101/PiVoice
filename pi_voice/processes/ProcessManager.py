from multiprocessing.synchronize import Event
from multiprocessing.sharedctypes import Synchronized
import multiprocessing as mp
from queue import Queue
from ctypes import c_int

from pi_voice.switcher.SensorSwitcher import SensorSwitcher
from pi_voice.switcher.ActionSwitcher import ActionSwitcher
from pi_voice.processes.AudioProcess import AudioProcess
from pi_voice.processes.WhisperProcess import WhisperProcess
from pi_voice.processes.GPT2Process import GPT2Process
from pi_voice.processes.DataRecordingProcess import DataRecordingProcess
from pi_voice.processes.PersonalizedCommandProcess import PersonalizedCommandProcess
from pi_voice.processes.TakeActionProcess import TakeActionProcess
from pi_voice.processes.ErrorHandling import ErrorHandlingThread
from concurrent.futures import ThreadPoolExecutor


class ProcessManager:
    def __init__(
        self,
        sensor_switcher: SensorSwitcher,
        action_switcher: ActionSwitcher,
    ) -> None:
        # switcher gets passed because it initializes devices
        self.sensor_switcher = sensor_switcher
        self.action_switcher = action_switcher

        # declaring pipes and events
        self.audio_pipe_sender, self.audio_pipe_receiver = mp.Pipe()
        self.whisper_pipe_sender, self.whisper_pipe_receiver = mp.Pipe()
        self.gpt2_pipe_sender, self.gpt2_pipe_receiver = mp.Pipe()
        self.recording_audio_finished_event: Event = mp.Event()
        self.transcription_finished_event: Event = mp.Event()
        self.action_prediction_finished_event: Event = mp.Event()

        # stop flag and active processes count for graceful shutdown
        self.error_queue: Queue = Queue()
        self.stop_flag: Event = mp.Event()
        self.active_processes_count: Synchronized = mp.Value(c_int, 0)

    def start(self):
        audio_p = AudioProcess(
            self.audio_pipe_sender,
            self.recording_audio_finished_event,
            self.error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        whisper_p = WhisperProcess(
            self.audio_pipe_receiver,
            self.whisper_pipe_sender,
            self.recording_audio_finished_event,
            self.transcription_finished_event,
            self.error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        gpt2_p = GPT2Process(
            self.whisper_pipe_receiver,
            self.gpt2_pipe_sender,
            self.transcription_finished_event,
            self.action_prediction_finished_event,
            self.error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        take_action_p = TakeActionProcess(
            self.sensor_switcher,
            self.gpt2_pipe_receiver,
            self.action_prediction_finished_event,
            self.error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        data_recording_p = DataRecordingProcess(
            self.sensor_switcher,
            self.gpt2_pipe_receiver,
            self.action_prediction_finished_event,
            self.error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        personalized_command_p = PersonalizedCommandProcess(
            self.sensor_switcher,
            self.action_switcher,
            self.error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        error_handling_thread = ErrorHandlingThread(
            self.error_queue,
            self.stop_flag,
            self.active_processes_count,
        )

        whisper_process = mp.Process(target=whisper_p.run)
        gpt2_process = mp.Process(target=gpt2_p.run)

        whisper_process.start()
        gpt2_process.start()

        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.submit(error_handling_thread.run)
            executor.submit(audio_p.run)
            executor.submit(data_recording_p.run)
            executor.submit(personalized_command_p.run)
            executor.submit(take_action_p.run)

        whisper_process.join()
        gpt2_process.join()

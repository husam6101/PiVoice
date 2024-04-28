from pi_voice import logger
from multiprocessing.synchronize import Event
from multiprocessing.sharedctypes import Synchronized
import multiprocessing as mp
from queue import Queue as q
from multiprocessing.queues import Queue as mq
from ctypes import c_int

from pi_voice.switcher.SensorSwitcher import SensorSwitcher
from pi_voice.switcher.ActionSwitcher import ActionSwitcher
from pi_voice.processes.AudioThread import AudioThread
from pi_voice.processes.WhisperProcess import WhisperProcess
from pi_voice.processes.GPT2Process import GPT2Process
from pi_voice.processes.DataRecordingThread import DataRecordingThread
from pi_voice.processes.PersonalizedCommandThread import PersonalizedCommandThread
from pi_voice.processes.TakeActionThread import TakeActionThread
from pi_voice.processes.ErrorHandling import ErrorHandlingThread
from pi_voice.processes.PipeToThreadQueuesManagerThread import PipeToThreadQueuesManagerThread as P2TQManagerThread
from concurrent.futures import ThreadPoolExecutor


class ProcessManager:
    def __init__(
        self,
        sensor_switcher: SensorSwitcher,
        action_switcher: ActionSwitcher,
    ):
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

        self.thread_error_queue: q = q()
        # self.p2q_sent_event: Event = Event(ctx=mp.get_context())
        self.take_action_queue: q = q()
        self.data_recording_queue: q = q()
        self.process_error_queue: mq = mq(ctx=mp.get_context())

        self.stop_flag: Event = mp.Event()
        self.active_processes_count: Synchronized = mp.Value(c_int, 0)

    def start(self):
        audio_thread = AudioThread(
            self.audio_pipe_sender,
            self.recording_audio_finished_event,
            self.thread_error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        whisper_p = WhisperProcess(
            self.audio_pipe_receiver,
            self.whisper_pipe_sender,
            self.recording_audio_finished_event,
            self.transcription_finished_event,
            self.process_error_queue,
            self.stop_flag,
            self.active_processes_count,
        )

        gpt2_p = GPT2Process(
            self.whisper_pipe_receiver,
            self.gpt2_pipe_sender,
            self.transcription_finished_event,
            self.action_prediction_finished_event,
            self.process_error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        p2tq_manager_thread = P2TQManagerThread(
            self.gpt2_pipe_receiver,
            self.action_prediction_finished_event,
            # self.p2q_sent_event,
            [
                self.take_action_queue,
                self.data_recording_queue
            ]
        )
        take_action_thread = TakeActionThread(
            self.action_switcher,
            self.take_action_queue,
            self.thread_error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        data_recording_thread = DataRecordingThread(
            self.sensor_switcher,
            self.data_recording_queue,
            self.thread_error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        personalized_command_thread = PersonalizedCommandThread(
            self.sensor_switcher,
            self.action_switcher,
            self.thread_error_queue,
            self.stop_flag,
            self.active_processes_count,
        )
        error_handling_thread = ErrorHandlingThread(
            self.thread_error_queue,
            self.process_error_queue,
            self.stop_flag,
            self.active_processes_count,
        )

        whisper_process = mp.Process(target=whisper_p.run)
        gpt2_process = mp.Process(target=gpt2_p.run)

        whisper_process.start()
        gpt2_process.start()

        with ThreadPoolExecutor(max_workers=12) as executor:
            executor.submit(error_handling_thread.run)
            executor.submit(audio_thread.run)
            executor.submit(p2tq_manager_thread.run)
            executor.submit(data_recording_thread.run)
            executor.submit(take_action_thread.run) 
            # executor.submit(personalized_command_thread.run)

        whisper_process.join()
        gpt2_process.join()

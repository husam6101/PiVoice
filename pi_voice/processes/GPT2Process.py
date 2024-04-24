from concurrent.futures import ThreadPoolExecutor
from multiprocessing.connection import PipeConnection
from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Event
from queue import Queue

from pi_voice.operators.GPTOperator import GPTOperator
from pi_voice.processes.ErrorHandling import ErrorSeverity


class GPT2Process:
    def __init__(
        self,
        whisper_pipe: PipeConnection,
        gpt2_pipe: PipeConnection,
        transcription_finished_event: Event,
        action_prediction_finished_event: Event,
        error_queue: Queue,
        stop_flag: Event,
        active_processes_count: Synchronized[int],
    ):
        self.whisper_pipe: PipeConnection = whisper_pipe
        self.gpt2_pipe: PipeConnection = gpt2_pipe
        self.transcription_finished_event: Event = transcription_finished_event
        self.action_prediction_finished_event: Event = action_prediction_finished_event
        self.gpt2: GPTOperator = GPTOperator()
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=2)
        self.error_queue: Queue = error_queue
        self.stop_flag: Event = stop_flag
        self.active_processes_count: Synchronized[int] = active_processes_count

    def run(self):
        self.active_processes_count += 1

        while True:
            if self.transcription_finished_event.wait(timeout=3):
                try:
                    transcript = self.whisper_pipe.recv()

                    try:
                        future = self.executor.submit(self.gpt2.predict, transcript)
                        action = future.result()
                    except Exception as e:
                        self.error_queue.put(
                            (str(e), "model_errors", ErrorSeverity.CRITICAL)
                        )
                        continue

                    self.gpt2_pipe.send(action)
                    self.action_prediction_finished_event.set()
                except Exception as e:
                    self.error_queue.put((str(e), "process_errors", ErrorSeverity.LOW))
                    continue
                finally:
                    self.transcription_finished_event.clear()

                if self.stop_flag.is_set():
                    self.active_processes_count -= 1
                    break
            elif self.stop_flag.is_set():
                self.active_processes_count -= 1
                break

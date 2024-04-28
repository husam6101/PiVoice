from concurrent.futures import ThreadPoolExecutor
from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Event
from multiprocessing.queues import Queue

from pi_voice.operators.GPTOperator import GPTOperator
from pi_voice.processes.ErrorHandling import ErrorSeverity
from pi_voice import logger


class GPT2Process:
    def __init__(
        self,
        whisper_pipe,
        gpt2_pipe,
        transcription_finished_event: Event,
        action_prediction_finished_event: Event,
        error_queue: Queue,
        stop_flag: Event,
        active_processes_count: Synchronized,
    ):
        self.whisper_pipe = whisper_pipe
        self.gpt2_pipe = gpt2_pipe
        self.transcription_finished_event: Event = transcription_finished_event
        self.action_prediction_finished_event: Event = action_prediction_finished_event
        self.gpt2: GPTOperator = GPTOperator()
        self.error_queue: Queue = error_queue
        self.stop_flag: Event = stop_flag
        self.active_processes_count: Synchronized = active_processes_count

    def run(self):
        self.active_processes_count.value += 1
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=2)

        while True:
            if self.transcription_finished_event.wait(timeout=3):
                try:
                    transcript = self.whisper_pipe.recv()
                    logger.info("Received transcript. Predicting action...")

                    future = self.executor.submit(self.gpt2.predict, transcript)
                    action = future.result()
                    logger.info("Action predicted: " + action)

                    logger.info("Sending action to next process...")
                    self.gpt2_pipe.send(action)
                    self.action_prediction_finished_event.set()
                except Exception as e:
                    self.error_queue.put(
                        (str(e), "model_errors", ErrorSeverity.CRITICAL)
                    )
                    continue
                finally:
                    self.transcription_finished_event.clear()

                if self.stop_flag.is_set():
                    self.active_processes_count.value -= 1
                    break
            elif self.stop_flag.is_set():
                self.active_processes_count.value -= 1
                break

from multiprocessing.synchronize import Event
from multiprocessing.sharedctypes import Synchronized
from queue import Queue

from concurrent.futures import ThreadPoolExecutor
from pi_voice.operators.WhisperOperator import WhisperOperator
from pi_voice.processes.ErrorHandling import ErrorSeverity


class WhisperProcess:
    def __init__(
        self,
        audio_pipe,  # entry point
        whisper_pipe,  # exit point
        recorded_audio_event: Event,
        transcription_finished_event: Event,
        error_queue: Queue,
        stop_flag: Event,
        active_processes_count: Synchronized,
    ):
        self.whisper_pipe = whisper_pipe
        self.audio_pipe = audio_pipe
        self.recorded_audio_event: Event = recorded_audio_event
        self.transcription_finished_event: Event = transcription_finished_event
        self.whisper: WhisperOperator = WhisperOperator()
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=2)
        self.error_queue: Queue = error_queue
        self.stop_flag: Event = stop_flag
        self.active_processes_count: Synchronized = active_processes_count

    def run(self):
        self.active_processes_count += 1
        
        while True:
            if self.recorded_audio_event.wait(timeout=2):
                try:
                    audio = self.audio_pipe.recv()
                
                    try:
                        future = self.executor.submit(self.whisper.process, audio)
                        transcript = future.result()
                    except Exception as e:
                        self.error_queue.put((str(e), "model_errors", ErrorSeverity.CRITICAL))
                        continue
                    
                    self.whisper_pipe.send(transcript)
                    self.transcription_finished_event.set()
                except Exception as e:
                    self.error_queue.put((str(e), "process_errors", ErrorSeverity.LOW))
                    continue
                finally:
                    self.recorded_audio_event.clear()
                
                if (self.stop_flag.is_set()):
                    self.active_processes_count -= 1
                    break
            elif (self.stop_flag.is_set()):
                self.active_processes_count -= 1
                break
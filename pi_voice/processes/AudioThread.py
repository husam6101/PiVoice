from multiprocessing.synchronize import Event
from multiprocessing.sharedctypes import Synchronized
from queue import Queue

from pi_voice.operators.AudioOperator import AudioOperator
from pi_voice.operators import logger
from pi_voice.processes.ErrorHandling import ErrorSeverity
from pi_voice.utils.common import retry_on_exception


class AudioThread:
    def __init__(
        self,
        audio_pipe,  # exit point
        recording_audio_finished_event: Event,
        error_queue: Queue,
        stop_flag: Event,
        active_processes_count: Synchronized,
    ):
        self.audio_op = AudioOperator()
        self.audio_pipe = audio_pipe
        self.recording_audio_finished_event: Event = recording_audio_finished_event
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
                audio = retry_on_exception(self._record_audio())
                logger.debug(audio)
                try:
                    if audio is None:
                        continue
                    
                    logger.info("Sending audio to whisper process...")
                    self.audio_pipe.send(audio)
                    self.recording_audio_finished_event.set()
                except Exception as e:
                    logger.info(f"Error sending audio to whisper process: {e}")
                    self.error_queue.put((str(e), "thread_errors", ErrorSeverity.LOW))
                    continue
            except Exception as e:
                logger.info(f"Error recording audio: {e}")
                self.error_queue.put((str(e), "thread_errors", ErrorSeverity.HIGH))

    def _record_audio(self):
        logger.info("Recording audio...")
        recording = self.audio_op.record_audio()
        return recording

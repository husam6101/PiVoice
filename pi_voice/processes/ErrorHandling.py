from multiprocessing.synchronize import Event
from multiprocessing.sharedctypes import Synchronized
from queue import Queue as q
from multiprocessing.queues import Queue as mq
import time
import signal
import atexit

from pi_voice import logger
from pi_voice.switcher.ActionSwitcher import ActionSwitcher
from concurrent.futures import ThreadPoolExecutor


class ErrorHandlingThread:
    def __init__(
        self,
        thread_error_queue: q,
        process_error_queue: mq,
        stop_flag: Event,
        active_process_count: Synchronized,
    ) -> None:
        self.thread_error_queue: q = thread_error_queue
        self.process_error_queue: mq = process_error_queue,
        self.stop_flag: Event = stop_flag
        self.active_process_count: Synchronized = active_process_count

    def run(self):
        # handle exit operations and signals
        atexit.register(self.end_all)
        signal.signal(signal.SIGINT, lambda signum, frame: self.end_all())

        # handle errors with thread executor
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(self._process_error_receiver_thread)
            executor.submit(self._thread_error_receiver_thread)
    
    def _process_error_receiver_thread(self):
        while True:
            logger.info("Waiting for process error queue...")
            message, group, severity = self.process_error_queue.get()

            self._handle_errors(message, group, severity)

    def _thread_error_receiver_thread(self):
        while True:
            logger.info("Waiting for thread error queue...")
            message, group, severity = self.thread_error_queue.get()

            self._handle_errors(message, group, severity)
    
    def _handle_errors(self, message, group, severity):
        if severity == ErrorSeverity.CRITICAL or severity == ErrorSeverity.HIGH:
            self.end_all()
            return
        elif severity == ErrorSeverity.MEDIUM:
            pass
        elif severity == ErrorSeverity.LOW:
            pass

        logger.error(message)

    def end_all(self):
        action_switcher = ActionSwitcher()

        self.stop_flag.set()
        while self.active_process_count.value > 0:
            time.sleep(1)

        logger.info("All processes have been stopped.")
        logger.info("Exiting Program...")

        action_switcher.reset_all()


class ErrorSeverity:
    CRITICAL = 1  # log and break immediately
    HIGH = 2  # log and break if failed retry logic
    MEDIUM = 3  # log if failed retry logic
    LOW = 4  # only log

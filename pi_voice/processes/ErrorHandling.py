from multiprocessing.synchronize import Event
from multiprocessing.sharedctypes import Synchronized
from queue import Queue
import time
import signal
import atexit

from pi_voice.operators import logger
from pi_voice.switcher.ActionSwitcher import ActionSwitcher


class ErrorHandlingThread:
    def __init__(
        self,
        error_queue: Queue,
        stop_flag: Event,
        active_process_count: Synchronized,
    ) -> None:
        self.error_queue: Queue = error_queue
        self.stop_flag: Event = stop_flag
        self.active_process_count: Synchronized = active_process_count

    def run(self):
        # handle exit operations and signals
        atexit.register(self.end_all)
        signal.signal(signal.SIGINT, lambda signum, frame: self.end_all())

        # handle errors
        while True:
            message, group, severity = self.error_queue.get()

            if severity == ErrorSeverity.CRITICAL or severity == ErrorSeverity.HIGH:
                self.end_all()
                break
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

from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Event
from queue import Queue

from pi_voice.processes.ErrorHandling import ErrorSeverity
from pi_voice.switcher.ActionSwitcher import ActionSwitcher
from pi_voice.utils.common import retry_on_exception
from pi_voice import logger


class TakeActionThread:
    def __init__(
        self,
        action_switcher: ActionSwitcher,
        data_queue: Queue,
        error_queue: Queue,
        stop_flag: Event,
        active_processes_count: Synchronized,
    ):
        self.action_switcher: ActionSwitcher = action_switcher
        self.data_queue: Queue = data_queue
        self.error_queue: Queue = error_queue
        self.stop_flag: Event = stop_flag
        self.active_processes_count: Synchronized = active_processes_count

    def run(self):
        self.active_processes_count.value += 1

        while True:
            try:
                action = self.data_queue.get(block=True, timeout=4)
                logger.info(f"Received {action}. Taking action...")

                retry_on_exception(self.action_switcher.take_action, action)

                logger.info("Action taken.")
            except Exception as e:
                self.error_queue.put((str(e), "device_errors", ErrorSeverity.HIGH))
                continue

            if self.stop_flag.is_set():
                self.active_processes_count.value -= 1
                break

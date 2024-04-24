from multiprocessing.connection import PipeConnection
from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Event
from queue import Queue

from pi_voice.processes.ErrorHandling import ErrorSeverity
from pi_voice.switcher.ActionSwitcher import ActionSwitcher
from pi_voice.utils.common import retry_on_exception


class TakeActionProcess:
    def __init__(
        self,
        action_switcher: ActionSwitcher,
        gpt2_pipe: PipeConnection,
        action_prediction_finished_event: Event,
        error_queue: Queue,
        stop_flag: Event,
        active_processes_count: Synchronized[int],
    ) -> None:
        self.action_switcher: ActionSwitcher = action_switcher
        self.gpt2_pipe: PipeConnection = gpt2_pipe
        self.action_prediction_finished_event: Event = action_prediction_finished_event
        self.error_queue: Queue = error_queue
        self.stop_flag: Event = stop_flag
        self.active_processes_count: Synchronized[int] = active_processes_count

    def run(self):
        self.active_processes_count += 1

        while True:
            if self.action_prediction_finished_event.wait(timeout=4):
                try:
                    action = self.gpt2_pipe.recv()

                    try:
                        retry_on_exception(self.action_switcher.take_action(action))
                    except Exception as e:
                        self.error_queue.put(
                            (str(e), "device_errors", ErrorSeverity.HIGH)
                        )
                        continue
                except Exception as e:
                    self.error_queue.put((str(e), "process_errors", ErrorSeverity.LOW))
                    continue
                finally:
                    self.action_prediction_finished_event.clear()

                if self.stop_flag.is_set():
                    self.active_processes_count -= 1
                    break
            elif self.stop_flag.is_set():
                self.active_processes_count -= 1
                break

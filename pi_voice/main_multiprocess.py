from pi_voice.switcher.SensorSwitcher import SensorSwitcher
from pi_voice.switcher.ActionSwitcher import ActionSwitcher
from pi_voice.processes.ProcessManager import ProcessManager


class MainProcess:
    def __init__(self):
        self.sensor_switcher: SensorSwitcher = SensorSwitcher()
        self.action_switcher: ActionSwitcher = ActionSwitcher()
        self.process_manager: ProcessManager = ProcessManager(
            self.sensor_switcher,
            self.action_switcher,
        )

    def start(self):
        self.process_manager.start()

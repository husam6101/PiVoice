from pi_voice.config import config
from pi_voice.devices.OutputDevice import OutputDevice


class ActionSwitcher:
    def __init__(self):
        self.light = OutputDevice(config["devices"]["light"])
        self.tv = OutputDevice(config["devices"]["screen"])
        self.fan = OutputDevice(config["devices"]["fan"])
        # self.is_ready_device = OutputDevice(config["devices"]["isReadyLight"])

    def take_action(self, argument):
        switcher = {
            "light_on": self._light_on,
            "light_off": self._light_off,
            "tv_on": self._tv_on,
            "tv_off": self._tv_off,
            "fan_on": self._fan_on,
            "fan_off": self._fan_off,
            "do_nothing": self._do_nothing,
        }
        return switcher.get(argument, self._do_nothing)()

    def _light_on(self):
        self.light.on()

    def _light_off(self):
        self.light.off()

    def _tv_on(self):
        self.tv.on()

    def _tv_off(self):
        self.tv.off()

    def _fan_on(self):
        self.fan.on()

    def _fan_off(self):
        self.fan.off()

    def _do_nothing(self):
        pass  # default

    def reset_all(self):
        self._light_off()
        self._tv_off()
        self._fan_off()
        # self.is_ready_device.off()

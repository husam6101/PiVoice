from pi_voice.config import config
from pi_voice.devices.OutputDevice import OutputDevice


class ActionSwitcher:
    def __init__(self):
        self.light = OutputDevice(config["devices"]["light"])
        # self.tv = OutputDevice(config["devices"]["screen"])
        self.fan = OutputDevice(config["devices"]["fan"])
        self.is_ready_device = OutputDevice(config["devices"]["isReadyLight"])

    def take_action(self, argument):
        switcher = {
            "light_on": self.light_on,
            "light_off": self.light_off,
            "tv_on": self.tv_on,
            "tv_off": self.tv_off,
            "fan_on": self.fan_on,
            "fan_off": self.fan_off,
            "do_nothing": self.do_nothing,
        }
        return switcher.get(argument, self.do_nothing)()

    def light_on(self):
        self.light.on()

    def light_off(self):
        self.light.off()

    def tv_on(self):
        pass
        self.tv_on()

    def tv_off(self):
        pass
        self.tv.off()

    def fan_on(self):
        self.fan.on()

    def fan_off(self):
        self.fan.off()

    def do_nothing(self):
        pass  # default

    def reset_all(self):
        self.light_off()
        # self.tv_off()
        self.fan_off()
        self.is_ready_device.off()

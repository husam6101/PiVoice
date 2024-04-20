from pi_voice.devices.TemperatureHumiditySensor import TemperatureHumiditySensor
from pi_voice.config import config


class SensorSwitcher:
    def __init__(self):
        self.temperature_humidity_sensor = TemperatureHumiditySensor(
            config["sensors"]["temperatureHumidity"])
        # init light sensor

    def get_data(self):
        temp, humidity = self.temperature_humidity_sensor.get_data()
        light = 0
        return temp, humidity, light

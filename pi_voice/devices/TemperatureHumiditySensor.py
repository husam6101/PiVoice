import platform
import random
from pi_voice.devices.RPiPinInterface import RPiPinInterface
# from pi_voice.operators import logger

if platform.system() != 'Windows':
    import adafruit_dht


class TemperatureHumiditySensor:
    def __init__(self, device_name):
        self.pin_interface = RPiPinInterface()
        gpios = self.pin_interface.get_gpios_for(device_name)
        if len(gpios) > 0:
            gpio = gpios[0]  # Assuming only one GPIO is needed

            if platform.system() != 'Windows':
                self.device = adafruit_dht.DHT22(gpio)
        else:
            raise ValueError("No GPIOs available for device: " + device_name)

    def get_data(self):
        if platform.system() != 'Windows':
            return self.device.temperature, self.device.humidity

        return random.uniform(5, 30), random.uniform(30, 70)

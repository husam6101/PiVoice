import platform
from pi_voice.devices.RPiPinInterface import RPiPinInterface

if platform.system() != 'Windows':
    import adafruit_dht
else:
    from pi_voice.mocks import adafruit_dht


class TemperatureHumiditySensor:
    def __init__(self, device_name):
        self.pin_interface = RPiPinInterface()
        gpios = self.pin_interface.get_gpios_for(device_name)
        if len(gpios) > 0:
            gpio = gpios[0]  # Assuming only one GPIO is needed

            self.device = adafruit_dht.DHT22(
                self.pin_interface.get_board_pin_from(gpio)
            )
        else:
            raise ValueError("No GPIOs available for device: " + device_name)

    def get_data(self):
        return self.device.temperature, self.device.humidity

import json
from pi_voice.config import config, get_path_from
# from pi_voice.operators import logger
import platform

import RPi.GPIO as GPIO
import board

GPIO.setmode(GPIO.BCM)


class RPiPinInterface:
    def __init__(self):
        self.config = self._read_config()

    def _read_config(self):
        if platform.system() != 'Windows':
            with open(get_path_from(config["pinConfig"]), 'r') as config_file:
                return json.load(config_file)["pins"]

        return {}

    def get_gpio_number_from(self, gpio_name):
        return int(gpio_name.strip("GPIO"))

    def get_gpios_for(self, device_name):
        if platform.system() != 'Windows':
            filtered_pin_configuration = [
                x for x in self.config.values()
                if "GPIO" in x["type"] and x["usedBy"] == device_name
            ]
            return [
                self.get_gpio_number_from(x["type"])
                for x in filtered_pin_configuration
            ]

        return [0]

    def setup_gpios_as_input_for(self, device_name):
        for pin in self.get_gpios_for(device_name):
            GPIO.setup(pin, GPIO.IN)

    def get_board_pin_from(pin_number):
        try:
            # Dynamically get the attribute from the board module
            return getattr(board, f"D{pin_number}")
        except AttributeError:
            print(f"Pin D{pin_number} does not exist.")
            return None

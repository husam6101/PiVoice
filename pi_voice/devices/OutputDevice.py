from pi_voice.devices.RPiPinInterface import RPiPinInterface

import RPi.GPIO as GPIO


class OutputDevice:
    def __init__(self, device_name):
        # Create an instance of RPiPinInterface
        self.rpi_pin_interface = RPiPinInterface()

        self.gpio = self.rpi_pin_interface.get_gpios_for(device_name)[0]
        print(self.gpio)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio, GPIO.OUT)

    def on(self):
        GPIO.output(self.gpio, GPIO.HIGH)
        print(GPIO.input(self.gpio))

    def off(self):
        GPIO.output(self.gpio, GPIO.LOW)
        print(GPIO.input(self.gpio))

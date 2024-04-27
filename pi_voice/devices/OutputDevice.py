from pi_voice.devices.RPiPinInterface import RPiPinInterface
import platform

if (platform.system() != "Windows"):
    import RPi.GPIO as GPIO
else:
    import pi_voice.mocks.GPIO as GPIO


class OutputDevice:
    def __init__(self, device_name):
        # Create an instance of RPiPinInterface
        self.rpi_pin_interface = RPiPinInterface()

        self.gpio = self.rpi_pin_interface.get_gpios_for(device_name)[0]
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio, GPIO.OUT)

    def on(self):
        GPIO.output(self.gpio, GPIO.HIGH)

    def off(self):
        GPIO.output(self.gpio, GPIO.LOW)

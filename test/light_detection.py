import RPi.GPIO as GPIO
import time

# Define GPIO pins for light sensors using BCM numbering
LIGHT_SENSOR_PIN_1 = 27
LIGHT_SENSOR_PIN_2 = 22

GPIO.setmode(GPIO.BCM)

# Function to measure the time a pin stays LOW
def rc_time(pin):
    count = 0
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(pin, GPIO.IN)
    start_time = time.time()
    while (GPIO.input(pin) == GPIO.LOW) and (time.time() - start_time < 1.0):
        count += 1
    return count

# Assuming you have verified your wiring is correct
try:
    # Calibrate by finding room light values (modify these after testing)
    room_light_1 = 100
    room_light_2 = 120

    while True:
        # Measure light based on how long the pin stays LOW
        light_count_1 = rc_time(LIGHT_SENSOR_PIN_1)
        light_count_2 = rc_time(LIGHT_SENSOR_PIN_2)

        # Adjust for room light and invert for intuitive reading
        relative_light_1 = room_light_1 - light_count_1
        relative_light_2 = room_light_2 - light_count_2

        print(f"Relative light level on Sensor 1: {relative_light_1} (higher is darker)")
        print(f"Relative light level on Sensor 2: {relative_light_2} (higher is darker)")
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting the program")
finally:
    GPIO.cleanup()


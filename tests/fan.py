import RPi.GPIO as GPIO
import time

# Setting up GPIO 17
GPIO_PIN = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

# Check and display the initial state of GPIO 17
initial_state = GPIO.input(GPIO_PIN)
print(f"Initial state of GPIO 17: {'HIGH' if initial_state else 'LOW'}")

# Set GPIO 17 to HIGH
print("Setting GPIO 17 to HIGH")
GPIO.output(GPIO_PIN, GPIO.HIGH)
time.sleep(5)  # Wait for 5 seconds

# Check and display the state of GPIO 17 after setting to HIGH
state_after_high = GPIO.input(GPIO_PIN)
print(f"State of GPIO 17 after setting to HIGH: {'HIGH' if state_after_high else 'LOW'}")

# Set GPIO 17 to LOW
print("Setting GPIO 17 to LOW")
GPIO.output(GPIO_PIN, GPIO.LOW)
time.sleep(5)  # Wait for 5 seconds

# Check and display the state of GPIO 17 after setting to LOW
state_after_low = GPIO.input(GPIO_PIN)
print(f"State of GPIO 17 after setting to LOW: {'HIGH' if state_after_low else 'LOW'}")

# Cleanup GPIO settings
GPIO.cleanup()





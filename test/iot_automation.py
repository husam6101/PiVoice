import RPi.GPIO as GPIO
import time
import board
import adafruit_dht

# GPIO pin setup
LED_PIN = 17  # GPIO pin for the LED
FAN_PIN = 26  # GPIO pin for the fan motor
LIGHT_SENSOR_PIN = 27  # Adjust as per your setup
TEMP_SENSOR_PIN =  board.D4  # Adjust as per your setup

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)

# Initialize the DHT sensor
dht_device = adafruit_dht.DHT22(TEMP_SENSOR_PIN)

# Function to get light sensor data
def get_light_level(pin):
    count = 0
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(pin, GPIO.IN)
    start_time = time.time()
    while (GPIO.input(pin) == GPIO.LOW) and (time.time() - start_time < 1.0):
        count += 1
    return count

# Main function
def main():
    try:
        while True:
            # Check light level
            light_level = get_light_level(LIGHT_SENSOR_PIN)
            if light_level > 100:  # Threshold for darkness
                GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on LED
            else:
		GPIO.output(LED_PIN, GPIO.LOW)  # Turn off LED

            # Check temperature
            try:
                temperature_c = dht_device.temperature
                if temperature_c > 22:
                    GPIO.output(FAN_PIN, GPIO.HIGH)  # Turn on fan
                else:
                    GPIO.output(FAN_PIN, GPIO.LOW)  # Turn off fan
            except RuntimeError as error:
                # Handle read errors from the sensor
                print(error.args[0])

            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting the program")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
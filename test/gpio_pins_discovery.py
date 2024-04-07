import RPi.GPIO as GPIO

# Initialize GPIO in BCM mode
GPIO.setmode(GPIO.BCM)

# List of all Raspberry Pi GPIO pins (adjust the list based on your model)
gpio_pins = list(range(2, 28))  # Adjust the range for your specific Raspberry Pi model

def check_gpio_pins():
    used_pins = []
    for pin in gpio_pins:
        try:
            GPIO.setup(pin, GPIO.IN)
            if GPIO.input(pin) == GPIO.HIGH:
                print(f"Pin {pin} might be used (detected HIGH).")
                used_pins.append(pin)
            else:
                print(f"Pin {pin} might be unused (detected LOW).")
        except Exception as e:
            print(f"Error checking pin {pin}: {e}")

    if used_pins:
        print(f"Pins potentially in use: {used_pins}")
    else:
        print("No pins detected as being in use.")

    # Clean up GPIO resources
    GPIO.cleanup()

if __name__ == "__main__":
    check_gpio_pins()




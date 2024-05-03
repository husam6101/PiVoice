import time
import board
import adafruit_dht

# List of GPIO pins to check
GPIO_PINS = [board.D2, board.D3, board.D4, board.D5, board.D6, board.D7, board.D8, board.D9,
             board.D10, board.D11, board.D12, board.D13, board.D16, board.D17, board.D18,
             board.D19, board.D20, board.D21, board.D22, board.D23, board.D24, board.D25, board.D26, board.D27]

def check_sensor(pin):
    try:
        dht_device = adafruit_dht.DHT22(pin)
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity
        print(f"Sensor detected on pin {pin}: Temp: {temperature_c}°C, Humidity: {humidity}%")
        return True
    except RuntimeError as error:
        return False

def main():
    print("Checking GPIO pins for connected DHT11 sensor...")
    found_sensor = False
    for pin in GPIO_PINS:
        if check_sensor(pin):
            found_sensor = True
            break

    if not found_sensor:
        print("No sensor found on any GPIO pin.")

if __name__ == "__main__":
    main()


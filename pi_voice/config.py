import os

# Define the base directory relative to this file location
base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration dictionary with relative paths
config = {
    "baseDirectory": base_directory,
    "pinConfig": "pin_config.json",
    "lgbm": {
        "dataset": "datasets/sensor_data.csv",
        "model": "models/lgbm.txt",
        "labelEncoder": "models/lgbm_label_encoder.pkl",
        "testSize": 0.2,
        "randomState": 42,
    },
    "audio": "output.mp3",
    "sensors": {
        "temperatureHumiditySensor": "adafruit_dht.DHT22",
        "lightIntensitySensor": "UUGear Light Sensor",
    },
    "devices": {
        "led": "LED",
        "fan": "Fan",
        "isReadyDevice": "KY-034 7 Color Flashing LED Module",
    },
}


def get_path_from(config_path):
    """
    Returns the absolute path for the given configuration path.

    Args:
        config_path (str): A key in the config dictionary pointing to a relative path or a path dictionary.

    Returns:
        str: The absolute path corresponding to the config path.
    """
    # Check if the config_path points to a nested dictionary
    if isinstance(config_path, dict):
        return {
            k: os.path.join(config["baseDirectory"], v) for k, v in config_path.items()
        }
    return os.path.join(config["baseDirectory"], config_path)

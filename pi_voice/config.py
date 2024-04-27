import os

# Define the base directory relative to this file location
base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration dictionary with relative paths
config = {
    "baseDirectory": base_directory,
    "pinConfig": "pin_config.json",
    "lgbm": {
        "dataset": "datasets/sensor_data.csv",
        "model": "models/lgbm/model.txt",
        "labelEncoder": "models/lgbm/label_encoder.pkl",
        "testSize": 0.2,
        "randomState": 42,
    },
    "gpt2": {
        "model": "models/gpt2",
        "labelMap": {
            "tv_off": 0,
            "tv_on": 1,
            "light_off": 2,
            "light_on": 3,
            "fan_off": 4,
            "fan_on": 5,
            "do_nothing": 6,
        },
    },
    "audio": "output.mp3",
    "sensors": {
        "temperatureHumidity": "DHT22",
        "lightIntensity": "UUGear Light Sensor",
    },
    "devices": {
        "screen": "<no-screen-yet>",
        "light": "Bulb",
        "fan": "Fan",
        "isReadyLight": "KY-034 7 Color Flashing LED Module",
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

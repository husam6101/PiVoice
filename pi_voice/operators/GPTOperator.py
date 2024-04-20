import random
from pi_voice.operators import logger


class GPTOperator:
    def __init__(self):
        pass

    def random_command(self, transcript):
        # replace with your list of strings
        command_list = [
            "light_on",
            "light_off",
            "tv_on",
            "tv_off",
            "fan_on",
            "fan_off",
            "do_nothing"]
        return random.choice(command_list)

from pi_voice import logger

import pi_voice.main_multiprocess

if __name__ == "__main__":
    pi_voice.main_multiprocess.MainProcess().start()

# from pi_voice.utils.common import retry_on_exception
# from pi_voice.switcher.ActionSwitcher import ActionSwitcher

# retry_on_exception(ActionSwitcher().take_action, "fan_off")
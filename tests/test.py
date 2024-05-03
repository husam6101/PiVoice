from pi_voice import logger
from pi_voice.config import config, get_path_from
from pi_voice.utils.common import (
    get_next_notable_timestamp,
    get_time_of_day_and_day_of_week,
    retry_on_exception,
)
from pi_voice.operators.DataOperator import DataOperator
from pi_voice.switcher.ActionSwitcher import ActionSwitcher
from pi_voice.switcher.SensorSwitcher import SensorSwitcher
from pi_voice.processes.PersonalizedCommandThread import PersonalizedCommandThread
from queue import Queue as q
import multiprocessing as mp
from ctypes import c_int

# import pi_voice.main_multiprocess

# if __name__ == "__main__":
#     pi_voice.main_multiprocess.MainProcess().start()

# retry_on_exception(get_next_notable_timestamp)

# print(retry_on_exception(SensorSwitcher().get_data))

# retry_on_exception(ActionSwitcher().take_action, ("light_off",))

PersonalizedCommandThread(
    SensorSwitcher(),
    ActionSwitcher(),
    q(),
    mp.Event(),
    mp.Value(c_int, 0)
).run()

# retry_on_exception(
#     DataOperator().add_row_to_csv,
#     (
#         get_path_from(config["lgbm"]["dataset"]),
#         ["temp", "humid", "light", "time_of_day", "day_of_week", "action"],
#     ),
# )

# DataOperator().add_row_to_csv(
#     *(
#         get_path_from(config["lgbm"]["dataset"]),
#         ["temp", "humid", "light", "time_of_day", "day_of_week", "action"],
#     )
# )

from pi_voice.operators import logger
logger.debug("Importing...")
from pi_voice.main_multiprocess import MainProcess
logger.debug("Imported!")
logger.debug("Starting...")

if __name__ == "__main__":
    MainProcess().start()
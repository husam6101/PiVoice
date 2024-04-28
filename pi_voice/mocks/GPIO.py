from pi_voice import logger

BCM = 'BCM'
BOARD = 'BOARD'
IN = 'IN'
OUT = 'OUT'
HIGH = 1
LOW = 0

def setmode(mode):
    pass

def setup(pin, direction):
    pass

def output(pin, value):
    logger.info(f"Mock GPIO: Setting {pin} to {value}")

def input(pin):
    pass

def cleanup():
    pass
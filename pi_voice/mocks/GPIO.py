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
    logger.debug(f"Mock GPIO: Setting pin {pin} to {'HIGH' if value == 1 else 'LOW'}")

def input(pin):
    pass

def cleanup():
    pass
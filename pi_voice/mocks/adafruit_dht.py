import random

class DHT22:
    temperature = random.randint(13, 29)
    humidity = random.randint(13, 29)
    
    def __init__(self, pin):
        self.pin = pin
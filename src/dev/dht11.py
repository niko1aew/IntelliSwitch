from machine import Pin
from time import time
from dht import DHT11

class Dht11:
    measureInterval = 5

    def __init__(self, pin, name='DHT'):
        self.temperature = -100
        self.humidity = -100
        self.name = name
        self.dhtPin = Pin(pin)
        self.dhtSensor = DHT11(self.dhtPin)
        self.getMeasure()

    def getMeasure(self):
        try:
            self.measureTime = time()
            self.dhtSensor.measure()
            temp,hum = self.dhtSensor.temperature(), self.dhtSensor.humidity()
            if all(isinstance(i, int) for i in [temp, hum]):
                self.temperature = temp
                self.humidity = hum
                return True
        except Exception as e:
            print('DHT11 error: '+str(e))
            if "[Errno 110]" in str(e):
                print("reinit sensor...")
                self.initDHT()
            return False

    def getState(self):
        timeDelta = time()-self.measureTime
        if timeDelta > self.measureInterval:
            self.getMeasure()
        if self.temperature != -100:
            return '{"dev_type":"dht11", "temperature":"'+str(self.temperature)+'","humidity":"'+str(self.humidity)+'"}'
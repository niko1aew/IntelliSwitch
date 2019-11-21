from machine import Pin

class Relay:
    def __init__(self, pin, name='Relay_1'):
        self.state = False
        self.name = name
        self.relayPin = Pin(pin, Pin.OUT)
        self.relayPin.on()

    def switchON(self):
        print("Switching relay ON")
        self.state = True
        self.relayPin.on()
        print(type(self.relayPin))
        print(self.relayPin)

    def switchOFF(self):
        print("Switching relay OFF")
        self.state = False
        self.relayPin.off()

    def switchState(self):
        self.state = not self.state
        self.relayPin.off() if self.state else self.relayPin.on()

    def getState(self):
        return '{"dev_type":"relay", "state":"on"}' if self.state \
            else '{"dev_type":"relay", "state":"off"}'
import RPi.GPIO as GPIO
# use P1 header pin numbering convention
GPIO.setmode(GPIO.BCM)


class Pumpe:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
    def __enter__(self):
        self.turnOn()
        print "Pumpe ein"
    def __exit__(self, type, value, traceback):
        self.turnOff()
        print "Pumpe aus"
    def turnOn(self):
        GPIO.output(self.pin, not True)
    def turnOff(self):
        GPIO.output(self.pin, not False)


vorlaufFussbodenheizung = Pumpe(7)


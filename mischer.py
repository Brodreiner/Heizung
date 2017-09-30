from time import sleep
import threading
import Queue

import RPi.GPIO as GPIO
# use P1 header pin numbering convention
GPIO.setmode(GPIO.BCM)


# Relais sind 0 aktiv
#
#  relay1     relay2
#               __auf
#      ________/
#   __          __
#     \__
#        zu
class Mischer(threading.Thread):
    def __init__(self, relay1, relay2):
        threading.Thread.__init__(self)
        self.relay1 = relay1
        self.relay2 = relay2
        # Set up the GPIO channels
        GPIO.setup(self.relay1, GPIO.OUT)
        GPIO.setup(self.relay2, GPIO.OUT)
        self.wasReset = False
        self.eventQueue = Queue.Queue()
        self.daemon = True
        self.stop()
        self.start() # thread starten

    def aufdrehen(self):
        if self.isZu:
            self.stop()
        GPIO.output(self.relay2, not True)
        self.isAuf = True
        
    def zudrehen(self):
        if self.isAuf:
            self.stop()
        GPIO.output(self.relay1, not False)
        self.isZu = True

    def stop(self):
        GPIO.output(self.relay2, not False)
        sleep(0.1)
        GPIO.output(self.relay1, not True)
        sleep(0.1)
        self.isAuf = False
        self.isZu = False

    def run(self):
        while True:
            mischerBefehl = self.eventQueue.get()
            mischerSchrittAuf = mischerBefehl[0]
            time = mischerBefehl[1]
            if mischerSchrittAuf:
                self.aufdrehen()
            else:
                self.zudrehen()
            sleep(time)
            if self.wasReset:
                self.wasReset = 0
            else:
                if self.eventQueue.empty():
                    self.stop()

    def schrittAuf(self, time):
        self.eventQueue.put((True, time))

    def schrittZu(self, time):
        self.eventQueue.put((False, time))

    def reset(self):
        with self.eventQueue.mutex:
            self.eventQueue.queue.clear()
        self.wasReset = False
        sleep(0.3)

vorlaufFussbodenheizung = Mischer(23, 25)


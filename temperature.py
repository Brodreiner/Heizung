################################################################
# This module cycically reads all 1-Wire temperature sensores
################################################################

import threading
import sys
import time
import sql

class TemperatureSensorError(Exception):
    pass


# startet die Temperaturmessung und gibt das Ergebnis zurueck
# die Funktion blockiert waehrend der Messung
# Schlaegt die Messung fehl, wird sie einige male wiederholt, ehe eine Exception geworfen wird
def getTemperature(sensorName):
    tries = 3
    while True:
        time.sleep(1)
        try:
            try:
                with open("/sys/bus/w1/devices/" + sensorName + "/w1_slave") as file:
                    lines = file.read().split("\n")
            except IOError:
                raise TemperatureSensorError("Temperatursensor nicht angeschlossen!")
            if lines[0][-3:] != "YES":
                raise TemperatureSensorError("Verbindung zum Temperatursensor verloren!")
            tempStringValue = lines[1].split(" ")[9][2:]
            if tempStringValue == "85000":
                raise TemperatureSensorError("Temperatursensor misst Mist: 85 Grad! Wers glaubt...")
            return float(tempStringValue)/1000.0
        except TemperatureSensorError as e:
            tries = tries - 1
            sys.stderr.write(str(e))
            if tries == 0:
                sql.reportError("ERROR", "TEMP_SENSOR", str(e) + " Temperaturmessung endgueltig fehlgeschlagen!")
                sys.stderr.write(" - Messung ist damit fehlgeschlagen!\n")
                raise
            else:
                sql.reportError("WARNING", "TEMP_SENSOR", str(e) + " Temperaturmessung wird noch " + str(tries) + " mal wiederholt!")
                sys.stderr.write(" - Messung wird noch " + str(tries) + " mal wiederholt!\n")



class TemperaturSensor(threading.Thread):
    def __init__(self, sensorId):
        threading.Thread.__init__(self)
        self.daemon = True
        self.sensorId = sensorId
        try:
            self.value = getTemperature(self.sensorId)
        except TemperatureSensorError:
            self.value = 99.9 # Wenn die Temperatur nicht ermittelt werden kann, gehe vom Schlimmsten aus!
        self.start()
    def run(self):
        global vorlaufFussbodenheizung
        while True:
            try:
                self.value = getTemperature(self.sensorId)
            except TemperatureSensorError:
                self.value = 99.9 # Wenn die Temperatur nicht ermittelt werden kann, gehe vom Schlimmsten aus!

vorlaufFussbodenheizung = TemperaturSensor("28-000004b8e80e")
#vorlaufFussbodenheizung = TemperaturSensor("28-0000053459d1")

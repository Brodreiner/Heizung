TEMPERATUR_SENSOR_ID = '28-000004b8e80e' # Originalsensor, der aktuell in im Mischer verbaut ist
#TEMPERATUR_SENSOR_ID = '28-0000053459d1' # Ersatzsensor, der an ein Netzwerkkabel gelötet ist

vorlauftemperatur = 99.9 # der Wert wird von diesem Modul automatisch zyklisch gemessen und aktualisert

import threading
import sys
from time import sleep

class TemperatureSensorError(Exception):
    pass


"""
Startet die Temperaturmessung und gibt das Ergebnis zurueck.
Die Funktion blockiert waehrend der Messung.
Schlaegt die Messung fehl, wird eine Exception geworfen.
"""
def leseTemperatursensorEinmal():
    try:
        with open("/sys/bus/w1/devices/" + TEMPERATUR_SENSOR_ID + "/w1_slave") as file:
            lines = file.read().split("\n")
    except IOError:
        raise TemperatureSensorError("Temperatursensor nicht gefunden!")
    if lines[0][-3:] != "YES":
        raise TemperatureSensorError("Verbindung zum Temperatursensor verloren!")
    tempStringValue = lines[1].split(" ")[9][2:]
    if tempStringValue == "0":
        raise TemperatureSensorError("Vorlauf ist eingefroren: 0 Grad! Wers glaubt...")
    if tempStringValue == "85000":
        raise TemperatureSensorError("Temperatursensor misst Mist: 85 Grad! Wers glaubt...")
    return float(tempStringValue)/1000.0

"""
Startet die Temperaturmessung und gibt das Ergebnis zurueck.
Die Funktion blockiert waehrend der Messung.
Schlaegt die Messung fehl, wird sie einige male wiederholt, ehe eine Exception geworfen wird.
"""
def leseTemperatursensorWiederholt():
    anzahlVersuche = 4
    while True:
        try:
            return leseTemperatursensorEinmal()
        except Exception as e:
            anzahlVersuche = anzahlVersuche - 1
            if anzahlVersuche == 0:
                raise
            else:
                sys.stderr.write(str(e))
                sys.stderr.write(" - Messung wird noch " + str(anzahlVersuche) + " mal wiederholt!\n")
                sleep(1)

"""
Dies ist die Thread-Klasse, die als Daemon gestartet wird.
Solange das Programm laeuft, liest der Thread Zyklisch den Temperatursensor aus
und aktualisiert die globale Variable 'temperatur'
"""
class TemperaturSensor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True # damit sich das Programm beenden kann, ohne dass der Temperatursensor-Thread beendet werden muss
    def run(self):
        global vorlauftemperatur
        while True:
            try:
                vorlauftemperatur = leseTemperatursensorEinmal()
            except Exception as e:
                sys.stderr.write(str(e) + ' - Sicherheitshalber nehmen wir 99.9 Grad an!\n')
                vorlauftemperatur = 99.9 # Wenn die Temperatur nicht ermittelt werden kann, gehe vom Schlimmsten aus!
            sleep(1)

temperaturSensor = TemperaturSensor()
temperaturSensor.start()

RELAIS_AUF_PIN = 18                   # Pin fuer das Relais, das den Mischermotor in auf-Richtung ansteuert
RELAIS_ZU_PIN = 16                    # Pin fuer das Relais, das den Mischermotor in zu-Richtung ansteuert

import atexit
import threading
from time import sleep
import RPi.GPIO as GPIO

#GPIO.setwarnings(False)               # keine Warnung, wenn die GPIOs beim letzen mal nicht aufgeraeumt wurden
GPIO.setmode(GPIO.BOARD)              # RPi.GPIO Layout verwenden (wie Pin-Nummern)
GPIO.setup(RELAIS_AUF_PIN, GPIO.OUT)
GPIO.setup(RELAIS_ZU_PIN, GPIO.OUT)
atexit.register(GPIO.cleanup)


mischerSekundenAuf = 0.0              # interner Werte, der mit mischerAuf() gesetzt werden kann
mischerSekundenZu = 0.0               # interner Werte, der mit mischerZu() gesetzt werden kann


"""
Signalisiet dem Mischer Thread, dass der Mischermotor fuer die gegebene Anzahl Sekunden in richtung Auf drehen soll.
Allerdings nur unter der Vorraussetzung dass der Mischer nicht gerade am Zu drehen ist.
"""
def mischerAuf(sekunden):
    global mischerSekundenAuf
    global mischerSekundenZu
    if mischerSekundenZu == 0:
        mischerSekundenAuf = max(mischerSekundenAuf, sekunden)

"""
Signalisiet dem Mischer Thread, dass der Mischermotor fuer die gegebene Anzahl Sekunden in richtung Zu drehen soll.
Zudrehen hat aus Sicherheitsgruenden immer Vorrang vor Aufdrehen.
"""
def mischerZu(sekunden):
    global mischerSekundenAuf
    global mischerSekundenZu
    mischerSekundenAuf = 0
    mischerSekundenZu = max(mischerSekundenZu, sekunden)

"""
Schaltet die Relais so, dass der Mischermotor in Richtung Auf dreht.
Die Funktion darft nur vom Mischer Thread selbst benutzt werden. (Raise condition)
"""
def relaisAuf():
    GPIO.output(RELAIS_ZU_PIN, GPIO.HIGH)  # Relais ist Low-Aktiv
    sleep(0.1)                             # Warte kurze Zeit, damit Motor nicht zu schnell Richtung wechseln muss
    GPIO.output(RELAIS_AUF_PIN, GPIO.LOW)  # Relais ist Low-Aktiv

"""
Schaltet die Relais so, dass der Mischermotor in Richtung Zu dreht.
Die Funktion darft nur vom Mischer Thread selbst benutzt werden. (Raise condition)
"""
def relaisZu():
    GPIO.output(RELAIS_AUF_PIN, GPIO.HIGH) # Relais ist Low-Aktiv
    sleep(0.1)                             # Warte kurze Zeit, damit Motor nicht zu schnell Richtung wechseln muss
    GPIO.output(RELAIS_ZU_PIN, GPIO.LOW)   # Relais ist Low-Aktiv

"""
Schaltet die Relais so, dass der Mischermotor stehen bleibt.
"""
def relaisNeutral():
    GPIO.output(RELAIS_AUF_PIN, GPIO.HIGH) # Relais ist Low-Aktiv
    GPIO.output(RELAIS_ZU_PIN, GPIO.HIGH)  # Relais ist Low-Aktiv


"""
Der Mischer Thread liest zyklisch die Sekundenwerte, die mit mischerAuf() und mischerZu() gesetzt wurden
und steuert entsprechend die Mischer Relais an.
"""
class MischerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True # damit sich das Programm beenden kann, ohne dass der Mischer-Thread beendet werden muss
    def run(self):
        global mischerSekundenAuf
        global mischerSekundenZu
        while True:
            if mischerSekundenZu:
                mischerSekundenZu = max(0, mischerSekundenZu - 0.1)
                relaisZu()
            elif mischerSekundenAuf:
                mischerSekundenAuf = max(0, mischerSekundenAuf - 0.1)
                relaisAuf()
            else:
                relaisNeutral()
                sleep(0.1)

# Mischer Thread wird automatisch beim Laden des Moduls gestartet
mischerThread = MischerThread()
mischerThread.start()

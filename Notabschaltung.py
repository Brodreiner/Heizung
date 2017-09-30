TEMPERATUR_NOTABSCHALTUNG = 44.0 # Ab welcher Temperatur soll der Mischer kommplett zu gedreht werden?

from time import sleep
import threading
import Temperatursensor
from Mischer import mischerZu

class Notabschaltung(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True # damit sich das Programm beenden kann, ohne dass der Notabschaltung-Thread beendet werden muss
    def run(self):
        sleep(2) # warte zwei Sekunden bevor die Ueberwachung aktiviert wird, damit der Temperatursensor Zeit hat das erste mal ausgelesen zu werden
        while True:
            if(Temperatursensor.vorlauftemperatur >= TEMPERATUR_NOTABSCHALTUNG):
                mischerZu(1)
                print("Notabschaltung: Temperatursensor.vorlauftemperatur=%.1f TEMP_NOTABSCHALTUNG=%.1f" % (Temperatursensor.vorlauftemperatur, TEMPERATUR_NOTABSCHALTUNG))
            sleep(1)

notabschaltung = Notabschaltung()
notabschaltung.start()

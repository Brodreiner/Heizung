"""
Dieses Modul fraegt automatisch zyklisch die aktuelle Aussentemperatur vom Wetterserver ab.
Mit dem Wert wird die globale Variable 'aussentemperatur' aktualisiert.
Wenn die Verbindung zum Wetterserver fehl schaegt, wird der letzte Wert so lange verwendet,
bis erneut eine Verbindung zustande kommt.
"""

aussentemperatur = 10.0 # Standardwert, der bei erfolgreicher Verbindung zum Wetterserver gleich ueberschrieben wird

import threading
import xml.etree.ElementTree as ET
from urllib import request
from time import sleep
import sys

class WetterError(Exception):
    pass

def holeAussentemperaturVomServer():
    url = "http://api.openweathermap.org/data/2.5/weather?q=Lochhausen&mode=xml&APPID=9acd9ad2302f1a6c2437b69ca19c7da5"

    try:
        xmlText = request.urlopen(url,timeout=5)
    except:
        raise WetterError("Wetter Server nicht erreichbar: " + url)
    try:
        temperaturInKelvin = ET.parse(xmlText).getroot().find("temperature").get("value")
        temperaturInCelsius = float(temperaturInKelvin) - 273.15
    except:
        raise WetterError("XML Dokument vom Wetter Server kann hat falsches Format!")
    return temperaturInCelsius

"""
Dies ist die Thread-Klasse, die als Daemon gestartet wird.
Solange das Programm laeuft, fraegt sie zyklisch den Wetter-Server ab
und aktualisiert die globale Variable 'aussentemperatur'
"""
class WetterThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True # damit sich das Programm beenden kann, ohne dass der WetterThread beendet werden muss
    def run(self):
        global aussentemperatur
        while True:
            try:
                aussentemperatur = holeAussentemperaturVomServer()
            except WetterError:
                sys.stderr.write(str(WetterError) + "\n")
            sleep(60) # es reicht, die Aussentemperatur einmal pro Minute abzufragen

wetterThread = WetterThread()
wetterThread.start()

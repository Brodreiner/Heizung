REGELINTERVALL = 10 # nur alle 10 Sekunden, soll der Mischermotor angesteuert werden werden
MAX_REGELDIFFERENZ = 10.0 # Nur maximal 10 Grad Regelabweichung werden beruecksichtigt, damit der Regler nicht zu agressiv regelt
HYSTERESE_VORLAUFTEMPERATUR = 0.8 # Temperaturbereich, innerhalb dem nicht nachgeregelt wird
STELLZEIT_PRO_KELVIN_TEMP_DIFF = 0.3; # Wie viele Sekunden soll der Mischermotor pro Kelvin Temperaturabweichung und Regelintervall angesteuert werden?

SOLL_VORLAUFTEMPERATUR_BEI_MINUS_10_GRAD = 42.0
SOLL_VORLAUFTEMPERATUR_BEI_PLUS_10_GRAD = 35.0

from time import sleep
import Temperatursensor
from Mischer import mischerAuf, mischerZu
import Wetter
from Notabschaltung import TEMPERATUR_NOTABSCHALTUNG

#####################################################################################################

SOLL_VORLAUFTEMPERATUR_BEI_0_GRAD = (SOLL_VORLAUFTEMPERATUR_BEI_MINUS_10_GRAD + SOLL_VORLAUFTEMPERATUR_BEI_PLUS_10_GRAD) / 2.0
SOLL_VORLAUFTEMPERATUR_STEIGUNG = (SOLL_VORLAUFTEMPERATUR_BEI_PLUS_10_GRAD - SOLL_VORLAUFTEMPERATUR_BEI_MINUS_10_GRAD) / 20.0    # negative Steigung

historie = []
historieString = ""

Schleifenzaehler = 0

sleep(3) # Bevor die Regelschleife startet, sollten wir warten, bis Temperatursensor gelesen und Aussentemperatur vom Server abgefragt wurden.

while(True):
    tAussen = Wetter.aussentemperatur
    tIst = Temperatursensor.vorlauftemperatur
    tSoll = min(SOLL_VORLAUFTEMPERATUR_BEI_0_GRAD + (SOLL_VORLAUFTEMPERATUR_STEIGUNG * tAussen), TEMPERATUR_NOTABSCHALTUNG - 1.0) # Vorlauftemperatur darf maximal 1 Grad unterhalb der Notabschaltung sein.
    tDelta = tIst - tSoll

    print("tAussen=%.1f" %tAussen, "tSoll=%.1f" %tSoll, "tIst=%.1f" %tIst, "tDelta=%+.1f" %tDelta, "Zyklus: {0:2d}/{1}".format(Schleifenzaehler%REGELINTERVALL+1, REGELINTERVALL), "Historie:", historieString)

    if Schleifenzaehler % REGELINTERVALL == 0: # Alle 10 Sekunden soll nachgeregelt werden
        tDeltaRegel = max(-MAX_REGELDIFFERENZ, min(tDelta, MAX_REGELDIFFERENZ)) # tDelta auf Regelbereich begrenzen
        if tDeltaRegel > HYSTERESE_VORLAUFTEMPERATUR:
            stellzeit = tDeltaRegel * STELLZEIT_PRO_KELVIN_TEMP_DIFF
            mischerZu(stellzeit)
            print("Mischer {0:.1f} Sekunden zu.".format(stellzeit))
        elif tDeltaRegel < -HYSTERESE_VORLAUFTEMPERATUR:
            stellzeit = -tDeltaRegel * STELLZEIT_PRO_KELVIN_TEMP_DIFF
            mischerAuf(stellzeit)
            print("Mischer {0:.1f} Sekunden auf.".format(stellzeit))

        # Historie
        historie.append(tIst - tSoll)
        if len(historie) > 10:
            del historie[0]
        historieString = ""
        for element in reversed(historie):
            if historieString:
                historieString += " "
            historieString += "{0:+.1f}".format(element)

    Schleifenzaehler = Schleifenzaehler + 1
    sleep(1)

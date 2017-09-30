REGELINTERVAL = 15
MAX_REGELDIFFERENZ = 10.0
ZULAESSIGE_TEMP_ABWEICHUNG = 0.8
#STELLZEIT_PRO_KELVIN_TEMP_DIFF = 1.2;
STELLZEIT_PRO_KELVIN_TEMP_DIFF = 0.3;
TEMP_NOTABSCHALTUNG = 44.0

import threading
import time
import pumpe
import wetter
import sql
import temperature
import mischer


class HeizungMainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        history = []
        isLetzteRichtungAuf = False

        # file log
        with open("logTempDeltaEveryMinute.txt", "a") as logfile:
            logfile.write("-------------------------restart-------------------------\n")


        with pumpe.vorlaufFussbodenheizung as pumpeVorlaufFussbodenheizung:
            aussentemperaturAlt = 10.0
            while(True):
                # ermittle vorlauf Solltemperatur aus Wetterdaten
                aussentemperatur = wetter.getOutdoorTemperature();
                # wenn die Messun fehlschlaegt, nimm den alten Wert
                if aussentemperatur:
                    aussentemperaturAlt = aussentemperatur
                else:
                    aussentemperatur = aussentemperaturAlt
                targetFeedTempAtMinusTenDegree = sql.getConfigValue("targetFeedTempAtMinusTenDegree")
                targetFeedTempAtPlusTenDegree = sql.getConfigValue("targetFeedTempAtPlusTenDegree")
                steigung = (targetFeedTempAtMinusTenDegree - targetFeedTempAtPlusTenDegree) / 20.0
                temperaturBei0Grad = targetFeedTempAtPlusTenDegree + (10 * steigung)
                vorlaufFussbodenheizungSoll = temperaturBei0Grad - (steigung * aussentemperatur)
                vorlaufFussbodenheizungSoll = min(vorlaufFussbodenheizungSoll, TEMP_NOTABSCHALTUNG - 1.0) # Vorlauftemperatur darf maximal 1 Grad unterhalb der Notabschaltung sein.

                # SQLite log
                sql.measurement_log(aussentemperatur, temperature.vorlaufFussbodenheizung.value, vorlaufFussbodenheizungSoll)

                # file log
                with open("logTempDeltaEveryMinute.txt", "a") as logfile:
                    tSoll = vorlaufFussbodenheizungSoll
                    tIst = temperature.vorlaufFussbodenheizung.value
                    tDelta = tIst - tSoll
                    logfile.write("aussentemperatur={0:+.1f}".format(aussentemperatur))
                    logfile.write(" tSoll={0:+.1f}".format(tSoll))
                    logfile.write(" tIst={0:+.1f}".format(tIst))
                    logfile.write(" tDelta={0:+.1f}".format(tDelta))

                    # tDelta auf Regelbereich begrenzen
                    if tDelta > MAX_REGELDIFFERENZ:
                        tDelta = MAX_REGELDIFFERENZ
                    if tDelta < -MAX_REGELDIFFERENZ:
                        tDelta = -MAX_REGELDIFFERENZ

                    if tDelta > ZULAESSIGE_TEMP_ABWEICHUNG:
                        stellzeit = tDelta * STELLZEIT_PRO_KELVIN_TEMP_DIFF
                        mischer.vorlaufFussbodenheizung.schrittZu(stellzeit)
                        print "Mischer {0:.1f} Sekunden zu.".format(stellzeit)
                        logfile.write("   Mischer {0:4.1f} Sekunden zu ".format(stellzeit))
                        if isLetzteRichtungAuf:
                            sql.reportError("INFO", "MIXER", "Richtungsaenderung: ZU")
                            isLetzteRichtungAuf = False
                            logfile.write("       Richtungsaenderung!")
                    elif tDelta < -ZULAESSIGE_TEMP_ABWEICHUNG:
                        stellzeit = -tDelta * STELLZEIT_PRO_KELVIN_TEMP_DIFF
                        mischer.vorlaufFussbodenheizung.schrittAuf(stellzeit)
                        print "Mischer {0:.1f} Sekunden auf.".format(stellzeit)
                        logfile.write("   Mischer {0:4.1f} Sekunden auf".format(stellzeit))
                        if not isLetzteRichtungAuf:
                            sql.reportError("INFO", "MIXER", "Richtungsaenderung: AUF")
                            isLetzteRichtungAuf = True
                            logfile.write("       Richtungsaenderung!")
                    else:
                        logfile.write("                            ")
                    logfile.write("\n")

                # history
                history.append(tIst - tSoll)
                if len(history) > 10:
                    del history[0]
                historyString = ""
                for element in reversed(history):
                    if historyString:
                        historyString += " "
                    historyString += "{0:+.1f}".format(element)

                for i in range(1,REGELINTERVAL+1):
                    tSoll = vorlaufFussbodenheizungSoll
                    tIst = temperature.vorlaufFussbodenheizung.value
                    tDelta = tIst - tSoll
                    if temperature.vorlaufFussbodenheizung.value > TEMP_NOTABSCHALTUNG:
                        mischer.vorlaufFussbodenheizung.reset()
                        mischer.vorlaufFussbodenheizung.zudrehen()
                        pumpe.vorlaufFussbodenheizung.turnOff()
                        sql.reportError("ERROR", "EMERGENCY_SHUTDOWN", "Notabschaltung wegen zu hoher Vorlauftemperatur: tMax=%f tIst=%f" % (TEMP_NOTABSCHALTUNG, temperature.vorlaufFussbodenheizung.value))
                        print "Notabschaltung!"
                    else:
                        pumpe.vorlaufFussbodenheizung.turnOn()
                    print "tAussen=%.1f" %aussentemperatur, "tSoll=%.1f" %tSoll, "tIst=%.1f" %tIst, "tDelta=%+.1f" %tDelta, "Zyklus: {0:2d}/{1}".format(i,REGELINTERVAL), "History:", historyString
                    time.sleep(1)

heizungMainThread = HeizungMainThread()


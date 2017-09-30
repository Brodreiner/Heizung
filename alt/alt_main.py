REGELINTERVAL = 0.5

import RPi.GPIO as GPIO
GPIO.setwarnings(False)
from time import sleep
import temperature
import mischer
vorlaufFussbodenheizungSoll = 40.0
import pickle
import os
import array
import itertools
SPRUNGANTWORT_FILENAME = "sprungantwort.txt"

ARRAY_SIZE = 360

#while True:
#	print temperature.vorlaufFussbodenheizung
#	sleep(1)

#mischer.vorlaufFussbodenheizung.schrittAuf()
#sleep(1)
#mischer.vorlaufFussbodenheizung.schrittZu()
#sleep(1)
#sleep(5)
#print "exit"
#exit()

def messeSprungantwort():
    sprungantwort = [0] * ARRAY_SIZE
    tempStart = temperature.vorlaufFussbodenheizung
    mischer.vorlaufFussbodenheizung.schrittAuf()
    for i in range(len(sprungantwort)):
        sprungantwort[i] = temperature.vorlaufFussbodenheizung - tempStart
        print sprungantwort[i], temperature.vorlaufFussbodenheizung
        sleep(REGELINTERVAL)
    return sprungantwort


sleep(1)

try:
    print "Versuche Sprungantwort aus Datei zu lesen."
    with open(SPRUNGANTWORT_FILENAME, "rb") as file:
        sprungantwort = pickle.load(file)
    print "Sprungantwort wurde erfolgreich aus Datei gelesen."
except IOError:
    print SPRUNGANTWORT_FILENAME, "nicht gefunden!"
    print "Sprungantwort wird jetzt ermittelt."
    sleep(1) # warte bis Temperatursensor bereit ist
    sprungantwort = messeSprungantwort()
    print "Sprungantwort wird jetzt gespeichert."
    with open(SPRUNGANTWORT_FILENAME, "wb") as file:
        pickle.dump(sprungantwort, file)


tSprungProMischerSchritt = sprungantwort[-1]
sprungantwortDiff = []
for i in sprungantwort:
    sprungantwortDiff.append(tSprungProMischerSchritt - i)

#print sprungantwortDiff


tVirtDelta = [0] * ARRAY_SIZE




try:
    while True:
        tSoll = vorlaufFussbodenheizungSoll
        tIst = temperature.vorlaufFussbodenheizung
        myMischer = mischer.vorlaufFussbodenheizung

        tDelta = tIst - tSoll

        print "tSoll=%.1f" %tSoll,"tIst=%.1f" %tIst,"tDelta=%.1f" %tDelta, "verschaetzt=%.1f" %(tDelta+tVirtDelta[0]), "tVirtDelta=[%.1f %.1f %.1f %.1f %.1f %.1f]" % (tVirtDelta[0], tVirtDelta[1], tVirtDelta[2], tVirtDelta[3], tVirtDelta[4], tVirtDelta[5])
        if tDelta + tVirtDelta[0] < -0.5 and tIst < tSoll:
            print "Mischer Schritt auf"
            myMischer.schrittAuf()
            tVirtDelta = [a+b for a,b in zip(tVirtDelta,sprungantwortDiff)]

        if tDelta + tVirtDelta[0] > 0.5:
            print "Mischer Schritt zu"
            myMischer.schrittZu()
            tVirtDelta = [a-b for a,b in zip(tVirtDelta,sprungantwortDiff)]
        tVirtDelta.pop(0)
        tVirtDelta.append(0)
        sleep(REGELINTERVAL-0.01)

except Exception as e:
    print e



# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import RPi.GPIO as GPIO
GPIO.setwarnings(False)
import subprocess
import mainloop
import time



import cherrypy
import cStringIO
import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
import matplotlib.dates
import datetime
import time
import threading
import sql
sql.reportError("INFO", "RESTART", "Die Heizungsregelung wurde neu gestartet!")

class HelloWorld(object):
    def index(self, resetErrorLog=None, saveTargetFeedTemp=None, targetFeedTempAtMinusTenDegree=None, targetFeedTempAtPlusTenDegree=None):
        if saveTargetFeedTemp:
            sql.setConfigValue("targetFeedTempAtMinusTenDegree", targetFeedTempAtMinusTenDegree)
            sql.setConfigValue("targetFeedTempAtPlusTenDegree", targetFeedTempAtPlusTenDegree)
            raise cherrypy.HTTPRedirect("")
        if resetErrorLog:
            sql.resetErrorLog()
            raise cherrypy.HTTPRedirect("")
        targetFeedTempAtMinusTenDegree = sql.getConfigValue("targetFeedTempAtMinusTenDegree")
        targetFeedTempAtPlusTenDegree = sql.getConfigValue("targetFeedTempAtPlusTenDegree")
        if not targetFeedTempAtMinusTenDegree:
            targetFeedTempAtMinusTenDegree = 40.0
        if not targetFeedTempAtPlusTenDegree:
            targetFeedTempAtPlusTenDegree = 32.0

        returnBuffer = cStringIO.StringIO()
        
        bytes = open("/tmp/tempPlot.png", "rb").read()
        returnBuffer.write("""<html><body>""")
        returnBuffer.write("""
        <form method="post">
            <table>
                <tr>
                    <th>Vorlauf1 bei -10&deg;C:</th>
                    <td><input type="text" name="targetFeedTempAtMinusTenDegree" value="%d"/></td>
                </tr>
                <tr>
                    <th>Vorlauf1 bei +10&deg;C:</th>
                    <td><input type="text" name="targetFeedTempAtPlusTenDegree" value="%d"/></td>
                </tr>
                <tr>
                    <th></th>
                    <td><input type="submit" name="saveTargetFeedTemp" value="speichern"/></td>
                </tr>
            </table>
        </form>
        """ % (targetFeedTempAtMinusTenDegree, targetFeedTempAtPlusTenDegree)
        )
        returnBuffer.write("""<img src="data:image/png;base64,%s"/>""" % bytes.encode("base64").strip())

        returnBuffer.write("""<br/><table border="1"><thead><tr><th>Datum / Uhrzeit</th><th>Fehlertyp</th><th>Fehlertext</th><tr><thead><tbody>""")
        errorHistory = sql.getLastWeekErrors()
        for timestamp, errorLevel, errorType, text in errorHistory:
            if errorLevel == "INFO":
                color = "white"
            elif errorLevel == "WARNING":
                color = "yellow"
            elif errorLevel == "ERROR":
                color = "red"
            else:
                color = "white"
            returnBuffer.write("""<tr style="background-color:%s"><td>%s</td><td>%s</td><td>%s</td></tr>""" % (color, timestamp, errorType, text))

        returnBuffer.write("""</tbody></table>""")
        returnBuffer.write("""<form method="post"><input type="submit" name="resetErrorLog" value="Fehlerspeicher l&ouml;schen"/></form>""")
        returnBuffer.write("""</body></html>""")

        return returnBuffer.getvalue()

    index.exposed = True

#cherrypy.server.socket_host = '0.0.0.0'
#cherrypy.quickstart(HelloWorld())
while(True):
    time.sleep(1)

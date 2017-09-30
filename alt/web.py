# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

globalLock = threading.Lock()

class HelloWorld(object):
    def index(self):
        with globalLock:
            x, outdoorTempLine, feedTempLine, targetTempLine  = zip(*sql.getLast24HourMeasurements())

            figure = matplotlib.pyplot.figure(figsize=(16, 12))

            figure.add_subplot(211).plot(x,feedTempLine,'-',x,targetTempLine,'--')
            figure.add_subplot(211).legend(['Vorlauftemperatur Ist', 'Volauftemperatur Soll'], loc='lower left')
            figure.add_subplot(211).grid()
            figure.add_subplot(211).tick_params(labeltop=False, labelright=True)

            figure.add_subplot(212).plot(x,outdoorTempLine,'-')
            figure.add_subplot(212).legend(['Außentemperatur'], loc='lower left')
            figure.add_subplot(212).grid()
            figure.add_subplot(212).tick_params(labeltop=False, labelright=True)

            sio = cStringIO.StringIO()
            figure.savefig(sio, format="png", bbox_inches='tight', pad_inches=0)

            retval =  """<html><body>
            <img src="data:image/png;base64,%s"/>
            </body></html>""" % sio.getvalue().encode("base64").strip()

            return retval

    index.exposed = True

cherrypy.server.socket_host = '0.0.0.0'
cherrypy.quickstart(HelloWorld())


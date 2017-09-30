# -*- coding: utf-8 -*-
from __future__ import unicode_literals

OUTPUT_FILENAME = "/tmp/tempPlot.png"

import os
import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
import matplotlib.dates
import datetime
import time
import sql

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
figure.savefig(OUTPUT_FILENAME + "temp", format="png", bbox_inches='tight', pad_inches=0)
os.rename(OUTPUT_FILENAME + "temp", OUTPUT_FILENAME)

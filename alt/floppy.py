#!/usr/bin/env python

from time import sleep
import os
import RPi.GPIO as GPIO

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

STEP_PIN = 17
DIRECTION_PIN = 27

MAX_STEPS = 50
g_stepCounter = 0

SPEEDUP = 2
TIME_SPACE = 30.0

GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIRECTION_PIN, GPIO.OUT)

notes = {"C": 65.41,
         "Des": 69.30,
         "D": 73.42,
         "Es": 77.78,
         "E": 82.41,
         "F": 87.31,
         "Ges": 92.50,
         "G": 98.00,
         "As": 103.83,
         "A": 110.00,
         "B": 116.54,
         "H": 123.57,
         "c": 130.81,
         "des": 138.59,
         "d": 146.83,
         "es": 155.56,
         "e": 164.81,
         "f": 174.61,
         "ges": 185.00,
         "g": 196.00,
         "as": 207.65,
         "a": 220.00,
         "b": 233.08,
         "h": 246.94,
        }

def initFloppy():
    GPIO.output(DIRECTION_PIN, False)
    for i in range(MAX_STEPS):
        GPIO.output(STEP_PIN,True)      
        sleep(0.01);
        GPIO.output(STEP_PIN,False)   


def playNote(note, timeInMilliSeconds):
    global g_stepCounter
    timeInMilliSeconds = timeInMilliSeconds / SPEEDUP
    if note == "":
        sleep(timeInMilliSeconds / 1000)
        return
    frequency = notes[note]
    if g_stepCounter < MAX_STEPS / 2:
        directionForward = True;
    else:
        directionForward = False;
    startTime = datetime.datetime.now()
    while True:
        GPIO.output(DIRECTION_PIN,directionForward)
        GPIO.output(STEP_PIN,True)      
        sleep(0.5/frequency);
        GPIO.output(STEP_PIN,False)   
        sleep(0.5/frequency);
        if directionForward:
            g_stepCounter = g_stepCounter + 1
        else:
            g_stepCounter = g_stepCounter - 1
        if g_stepCounter == MAX_STEPS or g_stepCounter == 0:
            print "change direction"
            directionForward = not directionForward
        currentTime = datetime.datetime.now()
        deltaTime = currentTime - startTime
        deltaTime = deltaTime / 1000
        if deltaTime.microseconds > timeInMilliSeconds - TIME_SPACE:
            sleep(TIME_SPACE / 1000.0)
            break

import datetime

initFloppy()
playNote("C",500)
playNote("D",500)
playNote("E",500)
playNote("F",500)
playNote("G",1000)
playNote("G",1000)

playNote("A",500)
playNote("A",500)
playNote("A",500)
playNote("A",500)
playNote("G",2000)

playNote("A",500)
playNote("A",500)
playNote("A",500)
playNote("A",500)
playNote("G",2000)

playNote("F",500)
playNote("F",500)
playNote("F",500)
playNote("F",500)

playNote("E",1000)
playNote("E",1000)

playNote("D",500)
playNote("D",500)
playNote("D",500)
playNote("D",500)

playNote("C",2000)

GPIO.cleanup()






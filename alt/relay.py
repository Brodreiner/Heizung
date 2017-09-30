from time import sleep
import RPi.GPIO as GPIO

# use P1 header pin numbering convention
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)


# Set up the GPIO channels
GPIO.setup(23, GPIO.OUT)


frequency = 1

while True:
    print "on"
    GPIO.output(23, True)
    sleep(0.5/frequency);
    print "off"
    GPIO.output(23, False)
    sleep(0.5/frequency);


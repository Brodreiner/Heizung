from time import sleep
import RPi.GPIO as GPIO

# use P1 header pin numbering convention
GPIO.setmode(GPIO.BCM)


# Set up the GPIO channels
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


frequency = 100

while True:
    print "Input:", GPIO.input(24)
    GPIO.output(23, GPIO.input(24))
    sleep(1.0/frequency);


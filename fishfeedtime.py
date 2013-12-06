#!/usr/bin/python
#
# Fishfeedtime powers down Powerheads/Filters/Pumps of your choice (which are connected to 433.92MHz power socket controllers)
# for a set duration.
#

## GPIO Pin Definitions
# Pin with button circuit GPIO Pullup
BUTTON = 17
# LED Pin if present...
LED = False
LEDPIN = 21
# Pin connect to 434MHz transmit Data Line. -- NOT CONFIGURABLE, connect to *** PIN26 // GPIO7 ***
##TRANS = 18
# Seconds to turn everything off for on button push:
OFFTIME = 300
# Do we have a buzzer here?
BUZZER = False
# If "True" - which GPIO Pin to use it?
BUZPIN = 23
# Where can the https://github.com/dmcg/raspberry-strogonanoff script be found?
switchscript = "./switch"
# List of dictionaries detailing channel and buttons for the desired controlled sockets:
SOCKETS = [ {"socket": "1"}, {"socket": "2"}, {"socket": "3"}, {"socket": "4"} ]


## Should setup the GPIO Pins Here / Import Libs
import time, os, sys
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
if BUZZER == True:
    GPIO.setup(BUZPIN, GPIO.OUT, False)
if LED == True:
    GPIO.setup(LEDPIN, GPIO.OUT, False)
GPIO.setup(BUTTON, GPIO.IN)


def sockets(state):
    sound_buzzer()
    if state == "on" or state == "off":
        print("Switching Sockets " + str(state))
        for a in SOCKETS:
            sock = str(a['socket'])
            switchcmd = str(switchscript) + " " + str(sock) + " " + str(state)
            print(switchcmd)
            os.system(switchcmd)
    else:
        print("Invalid state sent to sockets(): " + str(state))
        raise

def button_state():
    # If button not pressed (Open)
    if (GPIO.input(BUTTON)):
        return "Open"
    else:
        return "Closed"

def sound_buzzer():
    if BUZZER == True:
        # Make some noise!
        print("Beep")
        GPIO.output(BUZPIN, True)
        time.sleep(0.8)
        GPIO.output(BUZPIN, False)
    else:
        print("Buzzer not configured.")

def run_timer():
    sockets("off")
    count = 0
    # Insert a small time delay to ensure that devices are not immediately switched back on if button is held down.
    delay = 10
    time.sleep(delay)
    for x in (0, (int(OFFTIME) - delay)):
        if button_state() == "Closed":
            break
        if count == int(OFFTIME):
            break
        else:
            count = count + 1
            time.sleep(1)
    sockets("on")

## Actual run
# Check stragonanoff exists:
if not os.path.isfile(switchscript):
    print("Failed to locate " + str(switchscript))
    sys.exit(1)
try:
    while True:
        if button_state() == "Closed":
            run_timer()
except KeyboardInterrupt:
    print("Keyboard Interrupt. Enabling sockets.")
    sockets("on")
    GPIO.cleanup()
    print("Exiting...")
    sys.exit(0)


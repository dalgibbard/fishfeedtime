#!/usr/bin/python
#
# Fishfeedtime powers down Powerheads/Filters/Pumps of your choice (which are connected to 433.92MHz power socket controllers)
# for a set duration.
#

## GPIO Pin Definitions
# Pin with button circuit GPIO Pullup
BUTTON = 17
# LED Pin if present...
LED = True
LEDPIN = 24
# Pin connect to 434MHz transmit Data Line. -- NOT CONFIGURABLE, connect to *** PIN26 // GPIO7 ***
##TRANS = 18
# Seconds to turn everything off for on button push:
OFFTIME = 30
# Time (s) before OFFTIME to sound alert.
WARNTIME = 5
# Do we have a buzzer here?
BUZZER = False
# If "True" - which GPIO Pin to use it?
BUZPIN = 23
# Where can the https://github.com/dmcg/raspberry-strogonanoff script be found?
switchscript = "./switch"
# List of dictionaries detailing channel and buttons for the desired controlled sockets:
SOCKETS = [ {"socket": "1"}, {"socket": "2"}, {"socket": "3"}, {"socket": "4"} ]

# Set verbosity
VERBOSE = False

## Import needed modules
import time, os, sys
import RPi.GPIO as GPIO

## Detect early on that we're running with root permissions!
if not os.geteuid() == 0:
        sys.exit('Script must run as root')

# Setup GPIO
GPIO.setmode(GPIO.BCM)
if BUZZER == True:
    GPIO.setup(BUZPIN, GPIO.OUT, False)
if LED == True:
    GPIO.setup(LEDPIN, GPIO.OUT, False)
GPIO.setup(BUTTON, GPIO.IN)


def sockets(state):
    if state == "on" or state == "off":
        if VERBOSE == True:
            print("Switching Sockets " + str(state))
        for a in SOCKETS:
            sock = str(a['socket'])
            switchcmd = str(switchscript) + " " + str(sock) + " " + str(state)
            if VERBOSE == True:
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

def ledswitch(ledstate):
    if LED == True:
        if ledstate == "on":
            GPIO.output(LEDPIN, True)
        elif ledstate == "off":
            GPIO.output(LEDPIN, False)
        else:
            print("Invalid state passed to ledswitch: " + str(ledstate))
            raise
    else:
        if VERBOSE == True:
            print("LED not configured.")
     
def sound_buzzer():
    if BUZZER == True:
        # Make some noise!
        if VERBOSE == True:
            print("Beep")
        GPIO.output(BUZPIN, True)
        time.sleep(0.1)
        GPIO.output(BUZPIN, False)
    else:
        if VERBOSE == True:
            print("Buzzer not configured.")

def run_timer():
    ledswitch("on")
    sound_buzzer()
    sockets("off")
    count = 0
    # Insert a small time delay to ensure that devices are not immediately switched back on if button is held down.
    delay = 10
    time.sleep(delay)
    fulltime = int(OFFTIME - delay)
    warntime = int(fulltime - WARNTIME)
    while count <= fulltime:
        if VERBOSE == True:
            print("Count: " + str(count))
        if button_state() == "Closed":
            if VERBOSE == True:
                print("Button Push Override Detected.")
            break
        if count == fulltime:
            if VERBOSE == True:
                print("Duration completed.")
            break
        if count == warntime:
            if VERBOSE == True:
                print("Warning Time Reached.")
            sound_buzzer()
            time.sleep(0.3)
	    sound_buzzer()
	    time.sleep(0.3)
            sound_buzzer()
            # Increase by 2s, as buzzer takes some time :)
            count = count + 2
            time.sleep(1)
        else:
            count = count + 1
            time.sleep(1)

    sockets("on")
    ledswitch("off")

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
    print("\n\nKeyboard Interrupt. Ensuring sockets are Enabled...")
    sound_buzzer()
    time.sleep(0.2)
    sound_buzzer()
    sockets("on")
    ledswitch("off")
    GPIO.cleanup()
    print("Exiting...")
    sys.exit(0)


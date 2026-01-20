# main.py
# iBIT Board QC / Functional Test (MicroPython on BBC micro:bit)
#
# What this test does:
# - Button A: Reads analog pins (P0..P2) and iBIT external ADC channels (0..7) via iBIT.ReadADC()
# - Button B: Exercises motor forward/backward toggling and servo positions (SV1/SV2)
# - No button: Ensures motors and servos are stopped (safe state)
#
# Notes:
# - This script is intended for quick QC/validation after wiring or assembling an iBIT board.
# - Print output is visible in the MicroPython serial console.

from microbit import *
from iBIT import *  # Requires your iBIT.py library in the project

# iBIT MicroPython port (instance-based I2C address selection)
# - ibit = iBIT()        -> default address = IBIT_V2 (0x4A)
# - ibit = iBIT(0x48)    -> address = IBIT_V1 (0x48)
ibit = iBIT()

# Motor direction toggling state
direction_motor = 0          # 0 = FORWARD, 1 = BACKWARD
direction_time = 0           # Counts time slots to change behavior
spd = 60                     # Motor speed (0..100)
t0 = 0                       # Time reference for 500 ms periodic update


def showA():
    """Display an 'A' icon on the LED matrix."""
    display.show(Image('00900:'
                       '09090:'
                       '90009:'
                       '99999:'
                       '90009'))


def showB():
    """Display a 'B' icon on the LED matrix."""
    display.show(Image('99990:'
                       '90009:'
                       '99990:'
                       '90009:'
                       '99990'))
def showAll():
    """Display a 'All Pixels' icon on the LED matrix."""
    display.show(Image('99999:'
                       '99999:'
                       '99999:'
                       '99999:'
                       '99999'))

def direction_name(d):
    """Return a human-readable motor direction name."""
    if d == 0:
        return "FORWARD"
    elif d == 1:
        return "BACKWARD"
    else:
        return "UNKNOWN"

showAll()
# Main loop (runs forever)
while True:
    # Current time (ms since program start)
    t = running_time()

    # Execute control logic every 500 ms
    if (t - t0 >= 500):
        t0 = t

        # Toggle motor direction every 4 time slots (i.e., every 2 seconds)
        if direction_time % 4 == 0:
            direction_motor ^= 1
        direction_time += 1

        # ---------------------------
        # Button A: ADC read test
        # ---------------------------
        if button_a.is_pressed():
            showA()
            print("AN0-2 Read Test")
            an_labels = ["AN-0", "AN-1", "AN-2"]
            an_values = [pin0.read_analog(), pin1.read_analog(), pin2.read_analog()]
            print("[" + ", ".join(an_labels) + "]")
            print("[" + ", ".join("{:4d}".format(v) for v in an_values) + "]")
            print()

            print("ADC0-7 Read Test")
            adc_labels = ["ADC{}".format(i) for i in range(8)]
            adc_values = [ibit.ReadADC(i) for i in range(8)]  # Uses channel style: 0..7
            print("[" + ", ".join(adc_labels) + "]")
            print("[" + ", ".join("{:4d}".format(v) for v in adc_values) + "]")
            print()

        # ---------------------------
        # Button B: Motor + Servo test
        # ---------------------------
        if button_b.is_pressed():
            showB()
            print("Motor and Servo Test")
            print("DIRECTION = {},".format(direction_name(direction_motor)), "SPEED =", spd)

            # Alternate between running and stopping the motor every 500 ms
            if direction_time % 2 != 0:
                ibit.Motor(direction_motor, spd)
            else:
                ibit.MotorStop()

            # Swap servo targets based on direction
            if direction_motor:
                ibit.Servo(SV1, 60)
                ibit.Servo(SV2, 120)
                print("SV1 = 60 deg, SV2 = 120 deg")
            else:
                ibit.Servo(SV1, 120)
                ibit.Servo(SV2, 60)
                print("SV1 = 120 deg, SV2 = 60 deg")

        # ---------------------------
        # No button pressed: Safe state
        # ---------------------------
        else:
            ibit.MotorStop()
            ibit.ServoStop(SV1)
            ibit.ServoStop(SV2)
    sleep(10)
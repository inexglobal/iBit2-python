# iBIT MicroPython port (with "private" methods using __name mangling)
# + ReadADC() supports BOTH:
#   - ReadADC(0..7)         (channel number style)
#   - ReadADC(ADC0..ADC7)   (command byte style)
#   - Otherwise returns -1
#
# Hardware mapping (per your MakeCode extension):
# - Motor M1: DIR=P13, PWM=P14
# - Motor M2: DIR=P15, PWM=P16
# - Servo SV1: P8
# - Servo SV2: P12
# - ADC (ADS7828-like): I2C address 0x4A (default), command bytes per ibitReadADC enum
#
# Comments in English as requested.

from microbit import pin8, pin12, pin13, pin14, pin15, pin16, i2c, sleep

# ---------------------------
# Public constants (like enums)
# ---------------------------
FORWARD = 0
BACKWARD = 1

TURN_LEFT = 0
TURN_RIGHT = 1

SPIN_LEFT = 0
SPIN_RIGHT = 1

SV1 = 0
SV2 = 1

M1 = 0
M2 = 1

# ADC command bytes (matching your MakeCode enum values)
ADC0 = 132
ADC1 = 196
ADC2 = 148
ADC3 = 212
ADC4 = 164
ADC5 = 228
ADC6 = 180
ADC7 = 244

# I2C addresses
IBIT_V1 = 0x48
IBIT_V2 = 0x4A


class iBIT:
    # Default ADC address for iBIT V2.x
    ADC_ADDRESS = IBIT_V2

    # ---------------------------
    # "Private" / Internal methods (name mangling)
    # ---------------------------
    @staticmethod
    def __clamp(x, lo, hi):
        if x < lo:
            return lo
        if x > hi:
            return hi
        return x

    @staticmethod
    def __map_0_100_to_0_1023(speed_percent):
        """Map 0..100% to 0..1023 PWM duty."""
        s = iBIT.__clamp(int(speed_percent), 0, 100)
        return (s * 1023) // 100

    @staticmethod
    def __servo_write_deg(p, deg, us_min=500, us_max=2500):
        """
        Servo control for micro:bit MicroPython.
        - PWM period 20ms (50Hz)
        - Map 0..180 deg -> us_min..us_max pulse width
        - Convert to analog duty 0..1023
        """
        deg = iBIT.__clamp(int(deg), 0, 180)

        period_us = 20000  # 20ms
        p.set_analog_period_microseconds(period_us)

        pulse_us = us_min + (us_max - us_min) * deg // 180
        duty = pulse_us * 1023 // period_us
        duty = iBIT.__clamp(duty, 0, 1023)

        p.write_analog(duty)

    @staticmethod
    def __servo_stop(p):
        """Best-effort detach/stop PWM for servo on micro:bit."""
        p.write_analog(0)
        # Optional: force low (some setups behave better)
        p.write_digital(0)

    # ---------------------------
    # Public API (motor control)
    # ---------------------------
    @staticmethod
    def Motor(direction, speed):
        motorspeed = iBIT.__map_0_100_to_0_1023(speed)

        if direction == FORWARD:
            pin13.write_digital(1)
            pin14.write_analog(motorspeed)
            pin15.write_digital(0)
            pin16.write_analog(motorspeed)

        elif direction == BACKWARD:
            pin13.write_digital(0)
            pin14.write_analog(motorspeed)
            pin15.write_digital(1)
            pin16.write_analog(motorspeed)

    @staticmethod
    def Motor2(direction, speed1, speed2):
        ms1 = iBIT.__map_0_100_to_0_1023(speed1)
        ms2 = iBIT.__map_0_100_to_0_1023(speed2)

        if direction == FORWARD:
            pin13.write_digital(1)
            pin14.write_analog(ms1)
            pin15.write_digital(0)
            pin16.write_analog(ms2)

        elif direction == BACKWARD:
            pin13.write_digital(0)
            pin14.write_analog(ms1)
            pin15.write_digital(1)
            pin16.write_analog(ms2)

    @staticmethod
    def Turn(turn_dir, speed):
        motorspeed = iBIT.__map_0_100_to_0_1023(speed)

        if turn_dir == TURN_LEFT:
            pin13.write_digital(1)
            pin14.write_analog(0)
            pin15.write_digital(0)
            pin16.write_analog(motorspeed)

        elif turn_dir == TURN_RIGHT:
            pin13.write_digital(1)
            pin14.write_analog(motorspeed)
            pin15.write_digital(0)
            pin16.write_analog(0)

    @staticmethod
    def Spin(spin_dir, speed):
        motorspeed = iBIT.__map_0_100_to_0_1023(speed)

        if spin_dir == SPIN_LEFT:
            pin13.write_digital(0)
            pin14.write_analog(motorspeed)
            pin15.write_digital(0)
            pin16.write_analog(motorspeed)

        elif spin_dir == SPIN_RIGHT:
            pin13.write_digital(1)
            pin14.write_analog(motorspeed)
            pin15.write_digital(1)
            pin16.write_analog(motorspeed)

    @staticmethod
    def MotorStop():
        pin13.write_digital(1)
        pin14.write_analog(0)
        pin15.write_digital(1)
        pin16.write_analog(0)

    @staticmethod
    def setMotor(channel, direction, speed):
        motorspeed = iBIT.__map_0_100_to_0_1023(speed)

        if channel == M1 and direction == FORWARD:
            pin13.write_digital(1)
            pin14.write_analog(motorspeed)

        elif channel == M2 and direction == FORWARD:
            pin15.write_digital(0)
            pin16.write_analog(motorspeed)

        elif channel == M1 and direction == BACKWARD:
            pin13.write_digital(0)
            pin14.write_analog(motorspeed)

        elif channel == M2 and direction == BACKWARD:
            pin15.write_digital(1)
            pin16.write_analog(motorspeed)

    # ---------------------------
    # Public API (ADC)
    # ---------------------------
    @staticmethod
    def setADC_Address(addr):
        # addr should be IBIT_V1 (0x48) or IBIT_V2 (0x4A)
        iBIT.ADC_ADDRESS = addr

    @staticmethod
    def ReadADC(ch_or_cmd):
        """
        Accept:
          - 0..7 as channel number
          - ADC command byte (must be in the command table)
        Else:
          - return -1
        """
        __cmd_table = [ADC0, ADC1, ADC2, ADC3, ADC4, ADC5, ADC6, ADC7]

        x = int(ch_or_cmd)

        # 1) Channel number 0..7
        if 0 <= x <= 7:
            cmd = __cmd_table[x]

        # 2) Command byte must be one of known commands
        elif x in __cmd_table:
            cmd = x

        # 3) Invalid input
        else:
            return -1

        i2c.write(iBIT.ADC_ADDRESS, bytes([cmd]), repeat=False)
        data = i2c.read(iBIT.ADC_ADDRESS, 2, repeat=False)
        return (data[0] << 8) | data[1]

    # ---------------------------
    # Public API (Servo)
    # ---------------------------
    @staticmethod
    def Servo(which, degree):
        # Tune us_min/us_max if needed (e.g., 1000..2000 for some servos)
        if which == SV1:
            iBIT.__servo_write_deg(pin8, degree, us_min=500, us_max=2500)
        elif which == SV2:
            iBIT.__servo_write_deg(pin12, degree, us_min=500, us_max=2500)

    @staticmethod
    def ServoStop(which):
        if which == SV1:
            iBIT.__servo_stop(pin8)
        elif which == SV2:
            iBIT.__servo_stop(pin12)


# ---------------------------
# Optional: Example script (uncomment to test)
# ---------------------------
# # Servo test
# iBIT.Servo(SV1, 90)
# sleep(300)
# iBIT.Servo(SV2, 90)
# sleep(300)
#
# # Motor test
# iBIT.Motor(FORWARD, 50)
# sleep(1000)
# iBIT.MotorStop()
#
# # ADC test (both styles)
# print(iBIT.ReadADC(0))       # OK (channel)
# print(iBIT.ReadADC(ADC0))    # OK (command)
# print(iBIT.ReadADC(999))     # -1 (invalid)

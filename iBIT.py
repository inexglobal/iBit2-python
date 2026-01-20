# iBIT MicroPython port (instance-based I2C address selection)
# - ibit = iBIT()        -> default address = IBIT_V2 (0x4A)
# - ibit = iBIT(0x48)    -> address = IBIT_V1 (0x48)
#
# ReadADC() supports:
#   - ReadADC(0..7)         (channel number style)
#   - ReadADC(ADC0..ADC7)   (command byte style)
#   - Otherwise returns -1

from microbit import pin8, pin12, pin13, pin14, pin15, pin16, i2c

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
    def __init__(self, adc_address=IBIT_V2):
        """
        Create an iBIT object with a selectable ADC I2C address.

        Examples:
            ibit = iBIT()       # default 0x4A (IBIT_V2)
            ibit = iBIT(0x48)   # 0x48 (IBIT_V1)
        """
        self.ADC_ADDRESS = int(adc_address)

    # ---------------------------
    # "Private" / Internal methods (name mangling)
    # ---------------------------
    def __clamp(self, x, lo, hi):
        if x < lo:
            return lo
        if x > hi:
            return hi
        return x

    def __map_0_100_to_0_1023(self, speed_percent):
        """Map 0..100% to 0..1023 PWM duty."""
        s = self.__clamp(int(speed_percent), 0, 100)
        return (s * 1023) // 100

    def __servo_write_deg(self, p, deg, us_min=500, us_max=2500):
        """
        Servo control for micro:bit MicroPython.
        - PWM period 20ms (50Hz)
        - Map 0..180 deg -> us_min..us_max pulse width
        - Convert to analog duty 0..1023
        """
        deg = self.__clamp(int(deg), 0, 180)

        period_us = 20000  # 20ms
        p.set_analog_period_microseconds(period_us)

        pulse_us = us_min + (us_max - us_min) * deg // 180
        duty = pulse_us * 1023 // period_us
        duty = self.__clamp(duty, 0, 1023)

        p.write_analog(duty)

    def __servo_stop(self, p):
        """Best-effort detach/stop PWM for servo on micro:bit."""
        p.write_analog(0)
        p.write_digital(0)

    # ---------------------------
    # Public API (motor control)
    # ---------------------------
    def Motor(self, direction, speed):
        motorspeed = self.__map_0_100_to_0_1023(speed)

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

    def Motor2(self, direction, speed1, speed2):
        ms1 = self.__map_0_100_to_0_1023(speed1)
        ms2 = self.__map_0_100_to_0_1023(speed2)

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

    def Turn(self, turn_dir, speed):
        motorspeed = self.__map_0_100_to_0_1023(speed)

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

    def Spin(self, spin_dir, speed):
        motorspeed = self.__map_0_100_to_0_1023(speed)

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

    def MotorStop(self):
        pin13.write_digital(1)
        pin14.write_analog(0)
        pin15.write_digital(1)
        pin16.write_analog(0)

    def setMotor(self, channel, direction, speed):
        motorspeed = self.__map_0_100_to_0_1023(speed)

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
    def setADC_Address(self, addr):
        """Set ADC I2C address for this iBIT instance."""
        self.ADC_ADDRESS = int(addr)

    def ReadADC(self, ch_or_cmd):
        """
        Accept:
          - 0..7 as channel number
          - ADC command byte (must be in the command table)
        Else:
          - return -1
        """
        cmd_table = [ADC0, ADC1, ADC2, ADC3, ADC4, ADC5, ADC6, ADC7]
        x = int(ch_or_cmd)

        if 0 <= x <= 7:
            cmd = cmd_table[x]
        elif x in cmd_table:
            cmd = x
        else:
            return -1

        i2c.write(self.ADC_ADDRESS, bytes([cmd]), repeat=False)
        data = i2c.read(self.ADC_ADDRESS, 2, repeat=False)
        return (data[0] << 8) | data[1]

    # ---------------------------
    # Public API (Servo)
    # ---------------------------
    def Servo(self, which, degree):
        # Tune us_min/us_max if needed (e.g., 1000..2000 for some servos)
        if which == SV1:
            self.__servo_write_deg(pin8, degree, us_min=500, us_max=2500)
        elif which == SV2:
            self.__servo_write_deg(pin12, degree, us_min=500, us_max=2500)

    def ServoStop(self, which):
        if which == SV1:
            self.__servo_stop(pin8)
        elif which == SV2:
            self.__servo_stop(pin12)

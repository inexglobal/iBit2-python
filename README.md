# iBIT MicroPython library for i-BIT robot kit

powered by micro:bit

![i-BIT](icon487x487px.png)

The package adds support for the [i-BIT](https://inex.co.th/home/product/ibit/) controller board from Innovative Experiment [INEX](https://inex.co.th).

### micro:bit Pin Assignment

The following micro:bit pins are used for analog and digital sensors, DC motor drivers and servo motors:

* P0  -- Analog Input 0 (micro:bit default)
* P1  -- Analog Input 1 (micro:bit default)
* P2  -- Analog Input 2 (micro:bit default)
* P8  -- Digital Input/Output and PWM/Servo1 (SV1)
* P12 -- Digital Input/Output and PWM/Servo2 (SV2)
* P13 -- DigitalWrite Pin for DC motor control direction 1
* P14 -- AnalogWrite (PWM) Pin for DC motor speed control 1
* P15 -- DigitalWrite Pin for DC motor control direction 2
* P16 -- AnalogWrite (PWM) Pin for DC motor speed control 2
* P19 -- SCL connected to I2C-based 12-bit ADC chip (ADS7828-like)
* P20 -- SDA connected to I2C-based 12-bit ADC chip (ADS7828-like)

### Import and create iBIT instance

By default, iBIT() uses IBIT_V2 (0x4A).
If you want IBIT_V1 (0x48), pass the address to the constructor.

```
from microbit import *
from iBIT import *

ibit = iBIT()        # Default: IBIT_V2 (0x4A)
# ibit = iBIT(0x48)  # IBIT_V1 (0x48)
```
### Motor control

Use iBIT's motor function to drive motor forward and backward. The speed motor is adjustable between 0 to 100.

* The direction must be either FORWARD or BACKWARD
* Speed is an integer value between 0 - 100

```
from iBIT import *

ibit = iBIT()

ibit.Motor(FORWARD, 100)
ibit.Motor(BACKWARD, 100)
```

### Spin

Spin is used to control both motors separately. For example, one motor spins forward while the other spins backward.

* The Spin direction must be either SPIN_LEFT or SPIN_RIGHT
* Speed is an integer value between 0 - 100

```
from iBIT import *

ibit = iBIT()

ibit.Spin(SPIN_LEFT, 100)
ibit.Spin(SPIN_RIGHT, 100)
```

### Turn

The Turn function is used to control the robot movement by turning. One motor stops while the other motor runs (pivot turn).

* The Turn direction must be either TURN_LEFT or TURN_RIGHT
* Speed is an integer value between 0 - 100

```
from iBIT import *

ibit = iBIT()

ibit.Turn(TURN_LEFT, 100)
ibit.Turn(TURN_RIGHT, 100)
```
### Motor Stop

MotorStop is used to stop both motors. The speed is set to 0 automatically.

```
from iBIT import *

ibit = iBIT()
ibit.MotorStop()
```

### Servo

Use this function to control the servo angle from 0 to 180 degrees.

* Degree is an integer value between 0 - 180

```
from iBIT import *

ibit = iBIT()

ibit.Servo(SV1, 90)
ibit.Servo(SV2, 90)
```

### ReadADC

ReadADC reads the analog input data from the I2C-based ADC (ADS7828-like).
The conversion is typically 12-bit and often returns values in the range 0..4095.
iBIT provides 8-channel analog inputs with voltage range 0..3.3V.

* Analog sensor ports are ADC0 - ADC7
* Select analog channel 0 - 7 for reading the analog sensor.
* Use the analog value as conditions for the robot's mission.

### Example

* Read the analog input 0 and display the conversion data on micro:bit.
  User can change the analog channel any time.

```
from microbit import *
from iBIT import *

ibit = iBIT()
display.show(str(ibit.ReadADC(0)))  # ADC0
```
* Drive the motors with Forward and Backward by counting speed 0 - 100

```
from microbit import *
from iBIT import *

ibit = iBIT()

while True:
    for speed in range(0, 101):
        ibit.Motor(FORWARD, speed)
        sleep(50)

    for speed in range(0, 101):
        ibit.Motor(BACKWARD, speed)
        sleep(50)
```
* Drive the motors by pressing button A and B.
  Turn Left by speed 50 when pressed button A and Turn Right by speed 50 when pressed button B.

```
from microbit import *
from iBIT import *

ibit = iBIT()

while True:
    if button_a.was_pressed():
        ibit.Turn(TURN_LEFT, 50)

    if button_b.was_pressed():
        ibit.Turn(TURN_RIGHT, 50)

    sleep(10)
```
* Spin the motors by pressing button A and B.
  Spin Left by speed 50 when pressed button A and Spin Right by speed 50 when pressed button B.

```
from microbit import *
from iBIT import *

ibit = iBIT()

while True:
    if button_a.was_pressed():
        ibit.Spin(SPIN_LEFT, 50)

    if button_b.was_pressed():
        ibit.Spin(SPIN_RIGHT, 50)

    sleep(10)
```
* Example for Servo: drive SV1 and SV2 from 0 - 180 and then back to 0 again (repeat forever).

```
from microbit import *
from iBIT import *

ibit = iBIT()

while True:
    for deg in range(0, 181):
        ibit.Servo(SV1, deg)
        ibit.Servo(SV2, deg)
        sleep(10)

    for deg in range(180, -1, -1):
        ibit.Servo(SV1, deg)
        ibit.Servo(SV2, deg)
        sleep(10)
```
* Example for ServoStop (free servo mode).

```
from microbit import *
from iBIT import *

ibit = iBIT()

while True:
    if button_a.was_pressed():
        ibit.Servo(SV1, 90)

    if button_b.was_pressed():
        ibit.ServoStop(SV1)

    sleep(10)
```
## License

MIT

## Supported targets

* MicroPython for BBC micro:bit

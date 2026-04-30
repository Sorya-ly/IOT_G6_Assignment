from machine import Pin, I2C, PWM
import neopixel
import time
import tcs34725

# -------------------------------
# NeoPixel Setup
# -------------------------------
led = neopixel.NeoPixel(Pin(23), 24)

# -------------------------------
# Color Sensor Setup
# -------------------------------
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = tcs34725.TCS34725(i2c)

# -------------------------------
# Motor Setup (L298N)
# -------------------------------
IN1 = Pin(27, Pin.OUT)
IN2 = Pin(26, Pin.OUT)

ENA = PWM(Pin(14))
ENA.freq(1000)

print("Place object in front of sensor")

# -------------------------------
# LED Function
# -------------------------------
def show_color(color_name):
    if color_name == "RED":
        led.fill((255, 0, 0))
    elif color_name == "GREEN":
        led.fill((0, 255, 0))
    elif color_name == "BLUE":
        led.fill((0, 0, 255))
    else:
        led.fill((0, 0, 0))  # OFF

    led.write()
    print("Showing:", color_name)

# -------------------------------
# Motor Control Function
# -------------------------------
def motor_control(color_name):
    if color_name == "RED":
        IN1.value(1)
        IN2.value(0)
        ENA.duty(700)

    elif color_name == "GREEN":
        IN1.value(1)
        IN2.value(0)
        ENA.duty(500)

    elif color_name == "BLUE":
        IN1.value(1)
        IN2.value(0)
        ENA.duty(300)

    else:
        IN1.value(0)
        IN2.value(0)
        ENA.duty(0)  # stop

    print("Motor PWM:", ENA.duty())

# -------------------------------
# Main Loop
# -------------------------------
while True:
    r, g, b, c = sensor.read_raw()

    print("R:", r, "G:", g, "B:", b)

    # Threshold (no object)
    if r < 700 and g < 700 and b < 700:
        color = "OFF"

    # Color detection
    elif r > g and r > b:
        color = "RED"
    elif g > r and g > b:
        color = "GREEN"
    elif b > r and b > g:
        color = "BLUE"
    else:
        color = "OFF"

    # Output
    show_color(color)
    motor_control(color)

    time.sleep(1)

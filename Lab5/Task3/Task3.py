from machine import Pin, I2C
import neopixel
import time
import tcs34725

# Setup NeoPixel
led = neopixel.NeoPixel(Pin(23), 24)

# Setup Color Sensor
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = tcs34725.TCS34725(i2c)

print("Place object in front of sensor")

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

while True:
    r, g, b, c = sensor.read_raw()

    print("R:", r, " G:", g, " B:", b)

    # 🔥 Threshold condition
    if r < 700 and g < 700 and b < 700:
        color = "OFF"

    # 🎯 Classification Rules
    elif r > g and r > b:
        color = "RED"
    elif g > r and g > b:
        color = "GREEN"
    elif b > r and b > g:
        color = "BLUE"
    else:
        color = "OFF"

    # Show result on NeoPixel
    show_color(color)

    time.sleep(1)

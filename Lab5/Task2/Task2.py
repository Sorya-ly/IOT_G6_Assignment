from machine import Pin, I2C
import time
import tcs34725

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = tcs34725.TCS34725(i2c)

print("Place object in front of sensor")

while True:
    r, g, b, c = sensor.read_raw()

    # Determine color
    if r > g and r > b:
        color = "RED"
    elif g > r and g > b:
        color = "GREEN"
    elif b > r and b > g:
        color = "BLUE"
    else:
        color = "UNKNOWN"

    print("R:", r, " G:", g, " B:", b, " ->", color)

    time.sleep(1)

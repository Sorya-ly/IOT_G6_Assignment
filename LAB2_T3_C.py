# ====================
# IMPORTS
# ====================
import network
import socket
import time
from machine import Pin, SoftI2C, time_pulse_us
import dht
from machine_i2c_lcd import I2cLcd

# ====================
# WIFI CONFIG
# ====================
SSID = "project"
PASSWORD = "1234567890"

# ====================
# SENSOR SETUP
# ====================
# DHT11 (GPIO 4)
DHT_PIN = 4

# Ultrasonic
TRIG = Pin(27, Pin.OUT)
ECHO = Pin(26, Pin.IN)
TRIG.off()

# ====================
# LCD SETUP
# ====================
I2C_ADDR = 0x27
i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
lcd.clear()

lcd.putstr("Starting...")
time.sleep(2)
lcd.clear()

# ====================
# WIFI CONNECT
# ====================
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
lcd.putstr("Connecting WiFi")

timeout = 15
while not wifi.isconnected() and timeout > 0:
    time.sleep(1)
    timeout -= 1

if not wifi.isconnected():
    lcd.clear()
    lcd.putstr("WiFi Failed")
    raise RuntimeError("WiFi connection failed")

ip = wifi.ifconfig()[0]
print("WiFi connected")
print("Open browser at:", ip)

lcd.clear()
lcd.putstr("WiFi Connected")
lcd.move_to(0, 1)
lcd.putstr(ip)

time.sleep(2)
lcd.clear()

# ====================
# ULTRASONIC FUNCTION
# ====================
def get_distance_cm():
    TRIG.off()
    time.sleep_us(2)
    TRIG.on()
    time.sleep_us(10)
    TRIG.off()

    try:
        duration = time_pulse_us(ECHO, 1, 25000)
        if duration < 0:
            return "Out of range"
        distance = (duration * 0.0343) / 2
        return "{:.1f} cm".format(distance)
    except:
        return "Sensor error"

# ====================
# TEMPERATURE FUNCTION (FIXED)
# ====================
def get_temperature_c():
    try:
        time.sleep(2)  # IMPORTANT for DHT11 stability
        sensor = dht.DHT22(Pin(DHT_PIN))
        sensor.measure()
        temp = sensor.temperature()
        return "{} C".format(temp)
    except:
        return "DHT error"

# ====================
# WEB SERVER SETUP
# ====================
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 80))
server.listen(2)
server.settimeout(5)

print("Web server running...")

# ====================
# WEB PAGE
# ====================
html = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Sensor Control</title>
</head>
<body>
    <h2>ESP32 Sensor Control</h2>

    <form action="/distance">
        <button type="submit">Show Distance</button>
    </form>

    <br>

    <form action="/temp">
        <button type="submit">Show Temp</button>
    </form>
</body>
</html>
"""

# ====================
# MAIN LOOP
# ====================
while True:
    try:
        conn, addr = server.accept()
        request = conn.recv(1024).decode()
        print("Request:", request)

        if "/distance" in request:
            distance = get_distance_cm()
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("Distance:")
            lcd.move_to(0, 1)
            lcd.putstr(distance)

        elif "/temp" in request:
            temp = get_temperature_c()
            lcd.move_to(0, 1)
            lcd.putstr(" " * 16)     # clear line
            lcd.move_to(0, 1)
            lcd.putstr("Temp: " + temp)

        conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
        conn.send(html)
        conn.close()

    except OSError:
        pass

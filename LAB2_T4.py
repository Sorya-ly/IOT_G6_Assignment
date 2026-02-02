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
# DHT22
DHT_PIN = 4
dht_sensor = dht.DHT22(Pin(DHT_PIN))

# Ultrasonic
TRIG = Pin(5, Pin.OUT)
ECHO = Pin(18, Pin.IN)

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
print("Connected, IP:", ip)

lcd.clear()
lcd.putstr("WiFi Connected")
lcd.move_to(0, 1)
lcd.putstr(ip)
time.sleep(2)
lcd.clear()

# ====================
# LCD SCROLL FUNCTION
# ====================
def lcd_scroll_text(text, delay=0.4):
    lcd.clear()

    if len(text) <= 16:
        lcd.putstr(text)
        return

    padded = text + " " * 16
    for i in range(len(padded) - 15):
        lcd.clear()
        lcd.putstr(padded[i:i+16])
        time.sleep(delay)

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
# WEB PAGE
# ====================
def web_page():
    return """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 LCD Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h2>LCD Text Sender</h2>

    <form action="/" method="get">
        <input type="text" name="msg" placeholder="Enter text">
        <br><br>
        <input type="submit" value="Send">
    </form>

</body>
</html>
"""

# ====================
# WEB SERVER
# ====================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Web server running at http://", ip)

while True:
    conn, addr = s.accept()
    print("Client connected:", addr)

    request = conn.recv(1024).decode()
    print("Request:", request)

    if "GET /?msg=" in request:
        try:
            msg = request.split("GET /?msg=")[1].split(" ")[0]
            msg = msg.replace("+", " ")
            msg = msg.replace("%20", " ")

            print("LCD Message:", msg)
            lcd_scroll_text(msg)

        except:
            pass

    response = web_page()
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
    conn.send(response)
    conn.close()

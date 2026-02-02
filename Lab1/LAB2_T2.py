import network
import socket
import time
from machine import Pin, time_pulse_us
import dht

# ====================
# WIFI CONFIG
# ====================
SSID = "project"
PASSWORD = "1234567890"

# ====================
# SENSOR SETUP
# ====================
dht_sensor = dht.DHT11(Pin(4))

TRIG = Pin(27, Pin.OUT)
ECHO = Pin(26, Pin.IN)
TRIG.off()

# ====================
# WIFI CONNECT (SAFE RESET)
# ====================
wifi = network.WLAN(network.STA_IF)
wifi.active(False)
time.sleep(1)
wifi.active(True)
wifi.disconnect()
time.sleep(1)

wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
timeout = 15
while not wifi.isconnected() and timeout > 0:
    time.sleep(1)
    timeout -= 1

if not wifi.isconnected():
    raise RuntimeError("WiFi connection failed")

ip = wifi.ifconfig()[0]
print("WiFi connected")
print("Open browser at:", ip)

# ====================
# ULTRASONIC FUNCTION (SAFE)
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
# WEB SERVER SETUP
# ====================
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 80))
server.listen(2)
server.settimeout(5)

print("Web server running...")

# ====================
# MAIN LOOP
# ====================
while True:
    try:
        conn, addr = server.accept()
        conn.settimeout(3)
        print("Client connected:", addr)

        request = conn.recv(1024)
        if not request:
            conn.close()
            continue

        # ---- READ DHT11 SAFELY ----
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()
        except:
            temp = "N/A"
            hum = "N/A"

        # ---- READ ULTRASONIC ----
        dist = get_distance_cm()

        # ---- HTML RESPONSE ----
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Sensor Dashboard</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {{ font-family: Arial; text-align: center; }}
        h1 {{ color: #333; }}
        .box {{
            display: inline-block;
            padding: 20px;
            border: 2px solid #444;
            border-radius: 10px;
            font-size: 20px;
        }}
    </style>
</head>
<body>
    <h1>ESP32 Sensor Dashboard</h1>
    <div class="box">
        Temperature: {temp} &deg;C<br><br>
        Humidity: {hum} %<br><br>
        Distance: {dist}
    </div>
</body>
</html>
"""

        conn.sendall(
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n\r\n"
        )
        conn.sendall(html)
        conn.close()

    except Exception as e:
        print("Server error:", e)

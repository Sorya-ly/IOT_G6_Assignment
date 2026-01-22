import network
import urequests
import time
from machine import Pin
import dht

# ---------- WIFI ----------
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# ---------- TELEGRAM ----------
BOT_TOKEN = "8231699710:AAF01UR3dkMPL7d0NuW7ou9Z2jonBTkeCeM"
CHAT_ID = "-5095049406"

URL_SEND = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)

# ---------- DHT11 ----------
sensor = dht.DHT11(Pin(4))

# ---------- WIFI CONNECT ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected")

# ---------- MAIN LOOP ----------
while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        message = "Temperature: {:.2f} °C\nHumidity: {:.2f} %".format(temp, hum)

        urequests.post(URL_SEND, json={
            "chat_id": CHAT_ID,
            "text": message
        })

        print("Sent:", message)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)   # send every 5 seconds (change if needed)
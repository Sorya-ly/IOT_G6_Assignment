import network
import urequests
from machine import Pin
import dht
import time

# =====================
# CONFIGURATION
# =====================
WIFI_SSID = "Robotic WIFI"
WIFI_PASSWORD = "rbtWIFI@2025"

BOT_TOKEN = "8231699710:AAF01UR3dkMPL7d0NuW7ou9Z2jonBTkeCeM"
CHAT_ID = "-5095049406"

TELEGRAM_URL = "https://api.telegram.org/bot{}/".format(BOT_TOKEN)

TEMP_LIMIT = 20  # °C

# =====================
# HARDWARE SETUP
# =====================
DHT_PIN = 4
RELAY_PIN = 2   # ACTIVE LOW

sensor = dht.DHT11(Pin(DHT_PIN))
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(1)  # Relay OFF at start (ACTIVE LOW)

relay_on = False
auto_off_sent = False

# =====================
# WIFI CONNECTION
# =====================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        while not wlan.isconnected():
            time.sleep(1)

    print("WiFi connected:", wlan.ifconfig())

connect_wifi()

# =====================
# TELEGRAM FUNCTIONS
# =====================
def send_message(text):
    url = TELEGRAM_URL + "sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        r = urequests.post(url, json=payload)
        r.close()
    except Exception as e:
        print("Telegram send error:", e)

# =====================
# RELAY FUNCTIONS
# =====================
def relay_on_func():
    global relay_on
    relay.value(0)  # ACTIVE LOW → ON
    relay_on = True

def relay_off_func():
    global relay_on
    relay.value(1)  # OFF
    relay_on = False

# =====================
# STARTUP MESSAGE
# =====================
send_message("ESP32 online\nDHT11 monitoring started")

print("System started...")

# =====================
# MAIN LOOP
# =====================
while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        print("Temp:", temp, "°C | Humidity:", hum, "%")

        # ---------- TEMP >= LIMIT ----------
        if temp >= TEMP_LIMIT:
            auto_off_sent = False  # reset for next cooldown

            if not relay_on:
                print("ALERT: High temperature")
                send_message(
                    "ALERT!\nTemp ≥ {}°C\nRelay is OFF".format(TEMP_LIMIT)
                )

        # ---------- TEMP < LIMIT ----------
        else:
            if relay_on:
                relay_off_func()

                if not auto_off_sent:
                    print("Auto-OFF: Temp normal")
                    send_message(
                        "Temperature normal\nRelay auto-OFF"
                    )
                    auto_off_sent = True

        print("--------------------------")

    except OSError:
        print("Failed to read DHT11")

    time.sleep(5)
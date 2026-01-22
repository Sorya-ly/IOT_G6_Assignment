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

TEMP_LIMIT = 30  # °C

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
update_id = 0
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

def get_updates(offset):
    url = TELEGRAM_URL + "getUpdates?timeout=30&offset={}".format(offset)
    try:
        r = urequests.get(url)
        data = r.json()
        r.close()
        return data
    except Exception as e:
        print("Telegram getUpdates error:", e)
        return {"result": []}
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

def handle_commands():
    global update_id, relay_on

    updates = get_updates(update_id)
    for item in updates["result"]:
        update_id = item["update_id"] + 1  # update offset
        msg = item.get("message", {})
        text = msg.get("text", "")

        if text == "/on":
            relay.value(1)  # ACTIVE LOW → ON
            relay_on = True
            send_message("Relay turned ON")

        elif text == "/off":
            relay.value(0)  # OFF
            relay_on = False
            send_message("Relay turned OFF")
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
        handle_commands()
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        print("Temp:", temp, "°C | Humidity:", hum, "%")

        # ---------- TEMP >= LIMIT ----------
        if temp >= TEMP_LIMIT:
            auto_off_sent = False  # reset for next cooldown

            if not relay_on:
                print("ALERT: High temperature")
                send_message(" ALERT: High temperature, Relay: OFF")

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
import network
import time
from machine import Pin
import urequests as requests
from tm1637 import TM1637

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASSWORD = "rbtWIFI@2025"

BLYNK_TOKEN = "_OWGwNIr63Khm9cRWSgBJcO7VkS8nrk0"
BLYNK_API   = "http://blynk.cloud/external/api"

IR_PIN = 12
CLK_PIN = 17
DIO_PIN = 16

# ---------- HARDWARE ----------
ir_sensor = Pin(IR_PIN, Pin.IN)
display = TM1637(clk_pin=CLK_PIN, dio_pin=DIO_PIN, brightness=5)

# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)

print("Connecting WiFi...")
while not wifi.isconnected():
    time.sleep(1)
print("WiFi OK")

# ---------- BLYNK ----------
last_blynk_send = 0

def send_counter_to_blynk(value):
    global last_blynk_send

    # limit to 1 send per second
    if time.ticks_diff(time.ticks_ms(), last_blynk_send) < 1000:
        return

    last_blynk_send = time.ticks_ms()

    url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V0={value}"
    print("Send:", value)

    try:
        r = requests.get(url, timeout=3)
        r.close()
    except Exception as e:
        print("Send failed:", e)

# ---------- COUNTER ----------
counter = 0
display.show_number(counter)

last_trigger = 0

print("Running IR Counter")

# ---------- LOOP ----------
while True:

    if ir_sensor.value() == 0:
        now = time.ticks_ms()

        # debounce sensor
        if time.ticks_diff(now, last_trigger) > 600:
            last_trigger = now

            counter += 1
            print("Count:", counter)

            display.show_number(counter)
            send_counter_to_blynk(counter)

        while ir_sensor.value() == 0:
            time.sleep(0.05)

    time.sleep(0.05)

import network
import time
from machine import Pin
import urequests as requests
from tm1637 import TM1637

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASSWORD = "rbtWIFI@2025"

BLYNK_TOKEN = "_OWGwNIr63Khm9cRWSgBJcO7VkS8nrk0"
BLYNK_API = "http://blynk.cloud/external/api"

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

print("WiFi connected")

# ---------- BLYNK ----------
last_send = 0
last_mode_check = 0
ir_mode_enabled = 1   # default ON

def send_counter(value):
    global last_send
    if time.ticks_diff(time.ticks_ms(), last_send) < 1000:
        return
    last_send = time.ticks_ms()

    url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V0={value}"
    try:
        r = requests.get(url, timeout=3)
        r.close()
        print("Sent count:", value)
    except:
        print("Send failed")

def read_switch_v1():
    global last_mode_check, ir_mode_enabled

    # only check every 1 sec (avoid spam)
    if time.ticks_diff(time.ticks_ms(), last_mode_check) < 1000:
        return ir_mode_enabled

    last_mode_check = time.ticks_ms()

    url = f"{BLYNK_API}/get?token={BLYNK_TOKEN}&V1"
    try:
        r = requests.get(url, timeout=2)
        val = r.text.strip('[]')
        r.close()
        ir_mode_enabled = int(val)
        print("IR mode:", ir_mode_enabled)
    except:
        print("Switch read error")

    return ir_mode_enabled

# ---------- COUNTER ----------
counter = 0
display.show_number(counter)
last_trigger = 0

print("Task 5 system running")

# ---------- LOOP ----------
while True:

    mode = read_switch_v1()

    if mode == 1:
        # IR ENABLED
        if ir_sensor.value() == 0:
            now = time.ticks_ms()

            if time.ticks_diff(now, last_trigger) > 600:
                last_trigger = now
                counter += 1

                print("Count:", counter)
                display.show_number(counter)
                send_counter(counter)

            while ir_sensor.value() == 0:
                time.sleep(0.05)

    else:
        # IR DISABLED
        # sensor ignored
        pass

    time.sleep(0.05)

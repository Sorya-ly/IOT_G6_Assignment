import network
import time
import machine
import urequests as requests

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASSWORD = "rbtWIFI@2025"

BLYNK_TOKEN = "0Vf8blWu1obUzv1x88Gr-R2RIVvpdIjo"
BLYNK_API   = "http://blynk.cloud/external/api"

LED_PIN = 2
IR_PIN  = 12   # IR sensor OUT pin

# ---------- HARDWARE ----------
led = machine.Pin(LED_PIN, machine.Pin.OUT)
ir_sensor = machine.Pin(IR_PIN, machine.Pin.IN)

# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)
print("WiFi connected!")

# ---------- BLYNK ----------
def read_button_v4():
    r = requests.get(f"{BLYNK_API}/get?token={BLYNK_TOKEN}&V4")
    value = int(str(r.text).strip('[]"{}'))
    r.close()
    return value

def send_label_v2(text):
    text = text.replace(" ", "%20")  # URL encode spaces
    url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V2={text}"
    r = requests.get(url)
    r.close()

# ---------- MAIN ----------
print("Running IR Sensor + Blynk (Label Mode)...")

while True:
    # Button (V4) → LED
    if read_button_v4() == 1:
        led.on()
    else:
        led.off()

    # IR Sensor Reading
    ir_value = ir_sensor.value()

    if ir_value == 0:
        print("Object Detected")
        send_label_v2("DETECTED")
    else:
        print("No Object")
        send_label_v2("NOT DETECTED")

    time.sleep(1)


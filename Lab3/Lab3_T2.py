import network
import time
from machine import Pin, PWM
import urequests as requests

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASSWORD = "rbtWIFI@2025"

BLYNK_TOKEN = "0Vf8blWu1obUzv1x88Gr-R2RIVvpdIjo"
BLYNK_API   = "http://blynk.cloud/external/api"

SERVO_PIN = 13

# ---------- HARDWARE ----------
servo = PWM(Pin(SERVO_PIN), freq=50)

# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)
print("WiFi connected!")

# ---------- BLYNK ----------
def read_slider_v5():
    """Read slider value from Blynk V5"""
    try:
        r = requests.get(f"{BLYNK_API}/get?token={BLYNK_TOKEN}&V5", timeout=0.5)
        value = int(str(r.text).strip('[]"{}'))
        r.close()
        return value
    except:
        return None

def angle_to_duty(angle):
    """Convert 0-180 degree to PWM duty"""
    return int(26 + (angle / 180) * (128 - 26))

# ---------- MAIN ----------
print("Running Servo Control via Blynk Slider (Continuous)...")

while True:
    slider_value = read_slider_v5()
    if slider_value is not None:
        # Directly move servo to slider value every loop
        servo.duty(angle_to_duty(slider_value))
        print("Servo angle:", slider_value)

    time.sleep(0.05)  # faster polling for smoother control

import time
from machine import Pin, PWM
import urequests as requests

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASSWORD = "rbtWIFI@2025"

BLYNK_TOKEN = "0Vf8blWu1obUzv1x88Gr-R2RIVvpdIjo"
BLYNK_API   = "http://blynk.cloud/external/api"

IR_PIN = 12
SERVO_PIN = 13

# ---------- HARDWARE ----------
ir_sensor = Pin(IR_PIN, Pin.IN)
servo = PWM(Pin(SERVO_PIN), freq=50)

# ---------- WIFI CONNECTION ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("WiFi Connected!")
print("IP Address:", wifi.ifconfig()[0])

# ---------- FUNCTIONS ----------

def angle_to_duty(angle):
    # Convert 0–180° to PWM duty for ESP32
    return int(26 + (angle / 180) * (128 - 26))

def send_label_v2(text):
    # Send IR status to Blynk Label (V2)
    text = text.replace(" ", "%20")
    url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V2={text}"
    try:
        r = requests.get(url, timeout=0.5)
        r.close()
    except:
        pass

# ---------- SERVO POSITIONS ----------
OPEN_ANGLE = 90
CLOSED_ANGLE = 0

# Start closed
servo.duty(angle_to_duty(CLOSED_ANGLE))

print("Task 3 System Running...")

# ---------- MAIN LOOP ----------
while True:

    ir_value = ir_sensor.value()

    if ir_value == 0:  # Object detected (IR active LOW)
        print("Object Detected")
        send_label_v2("DETECTED")

        # Open Servo
        print("Opening Servo...")
        servo.duty(angle_to_duty(OPEN_ANGLE))
        time.sleep(2)

        # Close Servo
        print("Closing Servo...")
        servo.duty(angle_to_duty(CLOSED_ANGLE))
        send_label_v2("NOT DETECTED")

        # Wait until object removed to prevent repeat trigger
        while ir_sensor.value() == 0:
            time.sleep(0.1)

    time.sleep(0.1)

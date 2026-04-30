
import time
import network
import urequests

# WiFi credentials
ssid = "Robotic WIFI"
password = "rbtWIFI@2025"

# Node-RED endpoint
node_red_url = "http://10.30.0.152:1880/fever"

# Connect WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

while not wifi.isconnected():
    print("Connecting to WiFi...")
    time.sleep(1)

print("WiFi Connected:", wifi.ifconfig())

while True:

    # Example body temperature (replace with real sensor value)
    body_temp = 33.0

    # Fever detection logic
    if body_temp >= 32.5:
        fever_flag = 1
    else:
        fever_flag = 0

    print("Body Temperature:", body_temp)
    print("Fever Flag:", fever_flag)
    print("-----------------------")

    # Send to Node-RED
    try:
        data = {
            "body_temp": body_temp,
            "fever_flag": fever_flag
        }

        response = urequests.post(node_red_url, json=data)
        response.close()

        print("Sent:", data)

    except Exception as e:
        print("Send failed:", e)

    time.sleep(2)

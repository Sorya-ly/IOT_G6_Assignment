
import time
import urequests
import network

# WiFi credentials
ssid = "Robotic WIFI"
password = "rbtWIFI@2025"

# Node-RED endpoint
node_red_url = "http://10.30.0.152:1880/gas"

# Connect WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

while not wifi.isconnected():
    print("Connecting to WiFi...")
    time.sleep(1)

print("WiFi Connected:", wifi.ifconfig())

# Configure ADC pin
mq5 = ADC(Pin(33))
mq5.atten(ADC.ATTN_11DB)
mq5.width(ADC.WIDTH_12BIT)

# Store last 5 readings
readings = []

while True:

    raw_value = mq5.read()

    readings.append(raw_value)

    if len(readings) > 5:
        readings.pop(0)

    avg_value = sum(readings) / len(readings)

    voltage = (raw_value / 4095) * 3.3

    # -----------------------------
    # Gas Risk Classification
    # -----------------------------
    if avg_value < 2100:
        risk_level = "SAFE"

    elif avg_value < 2600:
        risk_level = "WARNING"

    else:
        risk_level = "DANGER"

    print("Raw ADC:", raw_value)
    print("Voltage: {:.2f} V".format(voltage))
    print("Moving Average:", avg_value)
    print("Risk Level:", risk_level)
    print("----------------------")

    # Send data to Node-RED
    try:
        data = {
            "gas": avg_value,
            "risk_level": risk_level
        }

        response = urequests.post(node_red_url, json=data)
        response.close()

        print("Sent:", data)

    except Exception as e:
        print("Failed to send:", e)

    time.sleep(1)

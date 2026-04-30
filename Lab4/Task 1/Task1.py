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

# Configure ADC
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

    print("Raw ADC:", raw_value)
    print("Voltage: {:.2f} V".format(voltage))
    print("Moving Average:", avg_value)

    # Send to Node-RED
    try:
        data = {"gas": avg_value}

        response = urequests.post(node_red_url, json=data)

        print("Sent to Node-RED:", data)

        response.close()

    except Exception as e:
        print("Send failed:", e)

    print("----------------------")

    time.sleep(1)

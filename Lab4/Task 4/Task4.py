from machine import Pin, I2C, ADC
import time
import urequests
import network
import bmp280
import ds3231  # Your custom library

# -------------------------
# WiFi credentials
# -------------------------
ssid = "Robotic WIFI"
password = "rbtWIFI@2025"

# Node-RED endpoint
node_red_url = "http://10.30.0.152:1880/sensor_data"

# -------------------------
# Connect WiFi
# -------------------------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)
while not wifi.isconnected():
    print("Connecting to WiFi...")
    time.sleep(1)
print("WiFi Connected:", wifi.ifconfig())

# -------------------------
# I2C setup for BMP280 and DS3231
# -------------------------
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
bmp = bmp280.BMP280(i2c)
rtc = ds3231.DS3231(i2c)

# -------------------------
# MQ5 gas sensor setup
# -------------------------
mq5 = ADC(Pin(33))
mq5.atten(ADC.ATTN_11DB)
mq5.width(ADC.WIDTH_12BIT)

readings = []

# -------------------------
# Main loop
# -------------------------
while True:

    # --- MQ5 Gas sensor ---
    raw_value = mq5.read()
    readings.append(raw_value)
    if len(readings) > 5:
        readings.pop(0)
    avg_gas = sum(readings) / len(readings)

    # --- Gas Risk Classification ---
    if avg_gas < 2100:
        risk_level = "SAFE"
    elif avg_gas < 2600:
        risk_level = "WARNING"
    else:
        risk_level = "DANGER"

    # --- Body Temperature and Fever Flag ---
    body_temp = 33.0  # Example value; replace with actual sensor if available
    fever_flag = 1 if body_temp >= 32.5 else 0

    # --- BMP280 Pressure & Altitude ---
    pressure = bmp.pressure       # in hPa
    altitude = bmp.altitude       # in meters

    # --- DS3231 Timestamp ---
    year, month, day, hour, minute, second = rtc.get_time()
    timestamp = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        year, month, day, hour, minute, second
    )

    # --- Prepare Data for Node-RED ---
    data = {
        "avg_gas": avg_gas,
        "risk_level": risk_level,
        "body_temp": body_temp,
        "fever_flag": fever_flag,
        "pressure": pressure,
        "altitude": altitude,
        "timestamp": timestamp
    }

    # --- Send to Node-RED ---
    try:
        response = urequests.post(node_red_url, json=data)
        response.close()
        print("Sent:", data)
    except Exception as e:
        print("Failed to send:", e)

    # --- Wait 2 seconds before next reading ---
    time.sleep(2)

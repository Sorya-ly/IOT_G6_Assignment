from machine import Pin, PWM, SoftI2C, time_pulse_us
from machine_i2c_lcd import I2cLcd
from tm1637 import TM1637
import dht
import network
import socket
import time
from time import sleep, sleep_us
import urequests

# ==============================
# BLYNK SETUP
# ==============================
BLYNK_AUTH_TOKEN = "BQ8OpMHd8qF3DzIgC3Ok8AnRv0CN_awx"
BLYNK_API = "http://blynk.cloud/external/api"

def blynk_write(pin, value):
    try:
        url = "{}/update?token={}&{}={}".format(BLYNK_API, BLYNK_AUTH_TOKEN, pin, value)
        urequests.get(url).close()
    except:
        pass

# ==============================
# TELEGRAM BOT
# ==============================
BOT_TOKEN = "8231699710:AAF01UR3dkMPL7d0NuW7ou9Z2jonBTkeCeM"
CHAT_ID = "-5095049406"
telegram_url = "https://api.telegram.org/bot" + BOT_TOKEN
last_update_id = 0

def send_telegram(msg):
    try:
        url = telegram_url + "/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        urequests.post(url, json=data).close()
    except:
        pass

def check_telegram():
    global last_update_id, gate_open
    try:
        url = telegram_url + "/getUpdates?offset=" + str(last_update_id + 1)
        response = urequests.get(url)
        data = response.json()
        response.close()
        if data["result"]:
            for update in data["result"]:
                last_update_id = update["update_id"]
                message = update["message"].get("text", "")
                if message == "/status":
                    send_telegram("Gate: " + ("OPEN" if gate_open else "CLOSED"))
                    send_telegram("Available Slots: " + str(get_available_slots()))
                    read_dht()
                    send_telegram("Temp: {:.1f}°C\nHumidity: {:.1f}%".format(temperature, humidity))
                elif message == "/slots":
                    send_telegram("Available Slots: " + str(get_available_slots()))
                elif message == "/temp":
                    read_dht()
                    send_telegram("Temp: {:.1f}°C\nHumidity: {:.1f}%".format(temperature, humidity))
                elif message == "/open":
                    set_servo(SERVO_OPEN)
                    gate_open = True
                    send_telegram("Gate Opened")
                    blynk_write("V4", 1)
                elif message == "/close":
                    set_servo(SERVO_CLOSED)
                    gate_open = False
                    send_telegram("Gate Closed")
                    blynk_write("V4", 0)
    except:
        pass

# ==============================
# WIFI SETUP
# ==============================
ssid = "AI WIFI"
password = "AIetl@2025"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting WiFi...")
while not wifi.isconnected():
    sleep(1)
print("Connected:", wifi.ifconfig()[0])

# ==============================
# LCD SETUP
# ==============================
i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# ==============================
# TM1637 DISPLAY
# ==============================
tm = TM1637(clk_pin=17, dio_pin=16, brightness=5)

# ==============================
# DHT SENSOR
# ==============================
dht_sensor = dht.DHT11(Pin(15))

# ==============================
# ULTRASONIC SENSOR
# ==============================
TRIG = Pin(27, Pin.OUT)
ECHO = Pin(26, Pin.IN)

# ==============================
# IR SENSORS
# ==============================
IR_ENTRY = Pin(32, Pin.IN)
IR1 = Pin(13, Pin.IN)
IR2 = Pin(14, Pin.IN)
IR3 = Pin(33, Pin.IN)
TOTAL_SLOTS = 3

# ==============================
# SERVO
# ==============================
servo = PWM(Pin(19), freq=50)
SERVO_CLOSED = 26
SERVO_OPEN = 77

# ==============================
# LIGHT
# ==============================
light = Pin(2, Pin.OUT)
light.off()

# ==============================
# VARIABLES
# ==============================
gate_open = False
car_passed_entry = False
temperature = 0
humidity = 0
time_opened = 0
last_blynk_update = 0
last_telegram_check = 0

# ==============================
# FUNCTIONS
# ==============================
def set_servo(duty):
    servo.duty(int(duty))

def get_distance_cm():
    TRIG.value(0)
    sleep_us(2)
    TRIG.value(1)
    sleep_us(10)
    TRIG.value(0)
    duration = time_pulse_us(ECHO, 1, 30000)
    if duration < 0:
        return None
    return (duration * 0.0343) / 2

def get_available_slots():
    occupied = 0
    if IR1.value() == 0: occupied += 1
    if IR2.value() == 0: occupied += 1
    if IR3.value() == 0: occupied += 1
    return TOTAL_SLOTS - occupied

def read_dht():
    global temperature, humidity
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
    except:
        pass

def lcd_display(l1, l2):
    lcd.move_to(0,0)
    lcd.putstr("                ")
    lcd.move_to(0,0)
    lcd.putstr(l1[:16])
    lcd.move_to(0,1)
    lcd.putstr("                ")
    lcd.move_to(0,1)
    lcd.putstr(l2[:16])

def web_page():
    slots = get_available_slots()
    gate_status = "OPEN" if gate_open else "CLOSED"
    gate_color = "green" if gate_open else "red"
    read_dht()

    # Slot individual statuses
    slot1_status = "Occupied" if IR1.value() == 0 else "Free"
    slot2_status = "Occupied" if IR2.value() == 0 else "Free"
    slot3_status = "Occupied" if IR3.value() == 0 else "Free"

    slot1_color = "text-red-600" if IR1.value() == 0 else "text-green-600"
    slot2_color = "text-red-600" if IR2.value() == 0 else "text-green-600"
    slot3_color = "text-red-600" if IR3.value() == 0 else "text-green-600"

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Parking System</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{
                background: linear-gradient(135deg, #1f2937, #111827);
            }}
            .card {{
                transition: transform 0.3s, box-shadow 0.3s;
            }}
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            }}
        </style>
    </head>
    <body class="min-h-screen flex items-center justify-center py-10">
        <div class="max-w-6xl w-full px-4">
            <h1 class="text-5xl font-bold text-center text-white mb-10 tracking-wide">Smart IoT Parking System</h1>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <!-- Slots Card -->
                <div class="card bg-gray-800 text-white p-6 rounded-xl shadow-lg">
                    <h2 class="text-2xl font-semibold mb-4">Available Slots</h2>
                    <p class="text-6xl font-bold text-green-400 mb-2">{slots}</p>
                    <p class="mb-4 text-gray-300">out of {TOTAL_SLOTS}</p>
                    <ul class="space-y-2">
                        <li class="{slot1_color} font-semibold">Slot 1: {slot1_status}</li>
                        <li class="{slot2_color} font-semibold">Slot 2: {slot2_status}</li>
                        <li class="{slot3_color} font-semibold">Slot 3: {slot3_status}</li>
                    </ul>
                </div>

                <!-- Temperature Card -->
                <div class="card bg-gray-800 text-white p-6 rounded-xl shadow-lg">
                    <h2 class="text-2xl font-semibold mb-4">Temperature & Humidity</h2>
                    <p class="text-5xl font-bold text-orange-400">{temperature}°C</p>
                    <p class="text-lg text-gray-300 mt-2">Humidity: {humidity}%</p>
                </div>

                <!-- Gate Card -->
                <div class="card bg-gray-800 text-white p-6 rounded-xl shadow-lg flex flex-col justify-center items-center">
                    <h2 class="text-2xl font-semibold mb-4">Gate Status</h2>
                    <div class="w-24 h-24 rounded-full flex items-center justify-center bg-{gate_color}-600 text-white text-3xl font-bold animate-pulse">
                        {gate_status}
                    </div>
                </div>
            </div>
        </div>
        <script>
            setTimeout(function() {{ location.reload(); }}, 2000);
        </script>
    </body>
    </html>
    """
    return html
   


# ==============================
# WEB SERVER
# ==============================
addr = socket.getaddrinfo("0.0.0.0",80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(5)
server.settimeout(0.1)
print("Web server running")

# ==============================
# INITIAL STATE
# ==============================
set_servo(SERVO_CLOSED)
lcd_display("Smart Parking","System Ready")
tm.show_number(TOTAL_SLOTS)
sleep(2)

# ==============================
# MAIN LOOP
# ==============================
while True:
    current_time = time.time()

    # --- Telegram every 2s ---
    if current_time - last_telegram_check > 2:
        check_telegram()
        last_telegram_check = current_time

    # --- Sensor readings ---
    read_dht()
    distance = get_distance_cm()
    available_slots = get_available_slots()
    tm.show_number(available_slots)

    # --- Blynk updates every 2s ---
    if current_time - last_blynk_update > 2:
        blynk_write("V1", available_slots)
        blynk_write("V2", temperature)
        last_blynk_update = current_time

    # --- Gate logic using ultrasonic sensor ---
    if IR_ENTRY.value() == 0 and gate_open and not car_passed_entry:
        car_passed_entry = True

    if distance and distance <= 15 and not gate_open:
        if available_slots > 0:
            set_servo(SERVO_OPEN)
            gate_open = True
            car_passed_entry = False
            time_opened = current_time
            blynk_write("V4", 1)
            print("Gate opened")

    if gate_open and ((current_time - time_opened) >= 5 or car_passed_entry):
        set_servo(SERVO_CLOSED)
        gate_open = False
        car_passed_entry = False
        blynk_write("V4", 0)
        print("Gate closed")

    lcd_display("Slots: {}".format(available_slots),
                "Gate: {}".format("OPEN" if gate_open else "CLOSED"))

    # --- Web server non-blocking ---
    try:
        conn, addr = server.accept()
        request = conn.recv(1024).decode()
        if "/open" in request:
            set_servo(SERVO_OPEN)
            gate_open = True
            time_opened = current_time
            blynk_write("V4", 1)
        if "/close" in request:
            set_servo(SERVO_CLOSED)
            gate_open = False
            blynk_write("V4", 0)
        response = web_page()
        conn.send(b"HTTP/1.1 200 OK\r\n")
        conn.send(b"Content-Type: text/html\r\n")
        conn.send(b"Connection: close\r\n\r\n")
        conn.sendall(response.encode())
        conn.close()
    except:
        pass

    sleep(0.1)

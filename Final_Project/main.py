from machine import Pin, SoftI2C, ADC, PWM
import dht
import time
import network
from umqtt.simple import MQTTClient
import json
import neopixel
import urequests
import gc

# --- Pin Setup ---
DHT_PIN   = 33
GAS_PIN   = 35
BUZZ_PIN  = 12
RELAY_PIN = 15
NEO_PIN   = 23
NEO_COUNT = 27

# --- Buzzer type ---
ACTIVE_BUZZER = True

# --- Pins ---
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(0)

sensor = dht.DHT11(Pin(DHT_PIN))

gas = ADC(Pin(GAS_PIN))
gas.atten(ADC.ATTN_11DB)
gas.width(ADC.WIDTH_12BIT)

if ACTIVE_BUZZER:
    buzzer_pin = Pin(BUZZ_PIN, Pin.OUT)
    buzzer_pin.value(0)
else:
    buzzer_pwm = PWM(Pin(BUZZ_PIN))
    buzzer_pwm.duty(0)

# --- NeoPixel ---
np = neopixel.NeoPixel(Pin(NEO_PIN), NEO_COUNT)

def neo_red():
    for i in range(NEO_COUNT):
        np[i] = (255, 0, 0)
    np.write()

def neo_green():
    for i in range(NEO_COUNT):
        np[i] = (0, 255, 0)
    np.write()

def neo_off():
    for i in range(NEO_COUNT):
        np[i] = (0, 0, 0)
    np.write()

def neo_flash():
    neo_red()
    time.sleep_ms(200)
    neo_off()
    time.sleep_ms(200)

# --- I2C LCD ---
I2C_ADDR = 0x27
SDA_PIN  = 21
SCL_PIN  = 22
i2c = SoftI2C(sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=400000)

class LCD:
    EN = 0b00000100
    RW = 0b00000010
    RS = 0b00000001
    BL = 0b00001000

    def __init__(self, i2c, addr=0x27, rows=2, cols=16):
        self.i2c  = i2c
        self.addr = addr
        self.rows = rows
        self.cols = cols
        self._bl  = self.BL
        self._init()

    def _write_byte(self, b):
        self.i2c.writeto(self.addr, bytes([b | self._bl]))

    def _pulse(self, b):
        self._write_byte(b | self.EN)
        time.sleep_us(1)
        self._write_byte(b & ~self.EN)
        time.sleep_us(50)

    def _send(self, value, mode):
        high = (value & 0xF0) | mode
        low  = ((value << 4) & 0xF0) | mode
        self._pulse(high)
        self._pulse(low)

    def _cmd(self, cmd): self._send(cmd, 0)
    def _char(self, ch): self._send(ch, self.RS)

    def _init(self):
        time.sleep_ms(50)
        for v in (0x30, 0x30, 0x30, 0x20):
            self._pulse(v)
            time.sleep_ms(5)
        for cmd in (0x28, 0x0C, 0x06, 0x01):
            self._cmd(cmd)
            time.sleep_ms(2)

    def clear(self):
        self._cmd(0x01)
        time.sleep_ms(2)

    def move_to(self, row, col):
        offsets = [0x00, 0x40, 0x14, 0x54]
        self._cmd(0x80 | (offsets[row] + col))

    def write(self, text):
        for ch in text:
            self._char(ord(ch))

    def backlight(self, on=True):
        self._bl = self.BL if on else 0
        self._write_byte(0)

# --- Buzzer helpers ---
GAS_ALERT_THRESHOLD = 2000

def buzzer_on():
    if ACTIVE_BUZZER:
        buzzer_pin.value(1)
    else:
        buzzer_pwm.freq(2500)
        buzzer_pwm.duty(512)

def buzzer_off():
    if ACTIVE_BUZZER:
        buzzer_pin.value(0)
    else:
        buzzer_pwm.duty(0)

def buzzer_beep(times=3, on_ms=200, off_ms=100):
    for _ in range(times):
        buzzer_on()
        time.sleep_ms(on_ms)
        buzzer_off()
        time.sleep_ms(off_ms)

def gas_label(raw):
    if raw < 1000:   return "Clean"
    elif raw < 2000: return "Low"
    elif raw < 3000: return "Mid"
    else:            return "HIGH"

# --- LCD init ---
lcd = LCD(i2c, addr=I2C_ADDR, rows=2, cols=16)
lcd.clear()
lcd.move_to(0, 0)
lcd.write("  System Ready  ")
lcd.move_to(1, 0)
lcd.write("Connecting WiFi.")

# --- WiFi ---
ssid     = "YOUR_WIFI"
password = "YOUR_WIFI"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(1)
print("WiFi connected:", wlan.ifconfig())

# --- Telegram ---
BOT_TOKEN = "YOUR_TOKEN"
CHAT_ID   = "YOUR_ID"         
TG_URL    = f"https://api.telegram.org/bot{BOT_TOKEN}"

last_update_id = 0  # tracks Telegram messages

def tg_send(msg):
    gc.collect()
    try:
        url = f"{TG_URL}/sendMessage"
        r = urequests.post(url, json={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
        })
        if r.status_code != 200:
            print("Telegram error", r.status_code, ":", r.text)
        else:
            print("Telegram sent OK")
        r.close()
    except Exception as e:
        print("Telegram error:", e)
    gc.collect()

def tg_skip_backlog():
    """Fast-forward last_update_id to the most recent update so we don't
    spend ages processing old group messages at startup."""
    global last_update_id
    try:
        url = f"{TG_URL}/getUpdates?offset=-1&limit=1"
        r = urequests.get(url)
        raw = r.text
        r.close()
        if '"update_id"' in raw:
            uid_start = raw.find('"update_id":') + 12
            uid_end   = raw.find(',', uid_start)
            last_update_id = int(raw[uid_start:uid_end].strip())
            print("Skipped Telegram backlog, last_update_id =", last_update_id)
        else:
            print("No backlog to skip.")
    except Exception as e:
        print("Skip backlog error:", e)


def tg_get_updates():
    global last_update_id
    try:
        url = (f"{TG_URL}/getUpdates?offset={last_update_id + 1}"
               f"&timeout=1&limit=1"
               f"&allowed_updates=%5B%22message%22%5D")
        r = urequests.get(url)
        raw = r.text
        r.close()

        if '"update_id"' in raw:
            uid_start = raw.find('"update_id":') + 12
            uid_end   = raw.find(',', uid_start)
            last_update_id = int(raw[uid_start:uid_end].strip())
            if '"text":"/status' in raw:
                return "status"
    except Exception as e:
        print("Telegram poll error:", e)
    return None

def build_status_msg(gas_raw, temp, humi, person_detected, relay_active):
    gas_str  = gas_label(gas_raw)
    relay_str = "ON  (Auto shutoff)" if relay_active else "OFF"
    person_str = "Detected" if person_detected else "Not detected"
    return (
        f" <b>System Status</b>\n"
        f" Temp: {temp}°C   Humidity: {humi}%\n"
        f" Gas Level: {gas_raw} ({gas_str})\n"
        f" Person: {person_str}\n"
        f" Relay: {relay_str}"
    )

# --- MQTT ---
MQTT_BROKER = "10.30.0.249"  # your Mac's IP
MQTT_TOPIC  = b"camera/detection"

person_detected = False

def on_message(topic, msg):
    global person_detected
    try:
        data = json.loads(msg.decode())
        person_detected = data.get("detected", False)
        print("MQTT received:", data)
    except Exception as e:
        print("MQTT parse error:", e)

mqtt = MQTTClient("ESP32_Sub", MQTT_BROKER, port=1883, keepalive=60)
mqtt.set_callback(on_message)
mqtt.connect()
mqtt.subscribe(MQTT_TOPIC)
print("MQTT connected and subscribed!")

# --- Relay helpers ---
def relay_on():  relay.value(1)
def relay_off(): relay.value(0)

# --- Initial setup ---
lcd.clear()
lcd.move_to(0, 0)
lcd.write("  System Ready  ")
neo_green()
buzzer_beep(times=2, on_ms=100, off_ms=80)

# Read sensors once for boot message
time.sleep(2)
try:
    sensor.measure()
    boot_temp = sensor.temperature()
    boot_humi = sensor.humidity()
except:
    boot_temp = 0
    boot_humi = 0
boot_gas = gas.read()

tg_skip_backlog()

# Send boot status to Telegram once
tg_send(
    f" <b>System Booted!</b>\n"
    f" Temp: {boot_temp}°C   Humidity: {boot_humi}%\n"
    f" Gas Level: {boot_gas} ({gas_label(boot_gas)})\n"
    f" Person: Not detected\n"
    f" Relay: OFF\n\n"
    f"Send /status anytime to check."
)

# --- State tracking ---
last_sensor_check  = time.ticks_ms()
last_alert_sent    = time.ticks_ms()
last_telegram_poll = time.ticks_ms()
was_gas_high       = False
relay_active       = False
ALERT_INTERVAL_MS  = 5000   # alert every 5 seconds
POLL_INTERVAL_MS   = 2000   # poll Telegram every 2 seconds

# --- Main Loop ---
while True:
    mqtt.check_msg()

    now = time.ticks_ms()

    # Poll Telegram for /status command
    if time.ticks_diff(now, last_telegram_poll) >= POLL_INTERVAL_MS:
        last_telegram_poll = now
        cmd = tg_get_updates()
        if cmd == "status":
            try:
                sensor.measure()
                temp = sensor.temperature()
                humi = sensor.humidity()
            except:
                temp = 0
                humi = 0
            gas_raw = gas.read()
            tg_send(build_status_msg(gas_raw, temp, humi, person_detected, relay_active))

    # Read sensors every 2 seconds
    if time.ticks_diff(now, last_sensor_check) >= 2000:
        last_sensor_check = now

        gas_raw = gas.read()
        gas_str = gas_label(gas_raw)

        try:
            sensor.measure()
            temp = sensor.temperature()
            humi = sensor.humidity()
        except:
            temp = 0
            humi = 0

        print(f"Gas:{gas_raw} Temp:{temp}C Humi:{humi}% Person:{person_detected}")

        if gas_raw >= GAS_ALERT_THRESHOLD:
            buzzer_on()
            neo_flash()

            # Send alert every 5 seconds
            if time.ticks_diff(now, last_alert_sent) >= ALERT_INTERVAL_MS:
                last_alert_sent = now

                if person_detected:
                    relay_active = False
                    relay_off()
                    tg_send(
                        f" <b>GAS ALERT!</b>\n"
                        f" Gas Level: {gas_raw} ({gas_str})\n"
                        f" Person detected - please check immediately!\n"
                        f" Relay: OFF (manual action needed)"
                    )
                else:
                    relay_active = True
                    relay_on()
                    tg_send(
                        f" <b>GAS ALERT!</b>\n"
                        f" Gas Level: {gas_raw} ({gas_str})\n"
                        f" No person detected!\n"
                        f" Relay: ON - Gas tap auto shutoff activated!"
                    )

            # LCD update
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.write("!! GAS ALERT !!")
            lcd.move_to(1, 0)
            if person_detected:
                lcd.write("Person Present  ")
            else:
                lcd.write("AUTO SHUTOFF ON ")

            was_gas_high = True

        else:
            buzzer_off()
            relay_active = False
            relay_off()
            neo_green()

            # Gas just recovered — send recovery message once
            if was_gas_high:
                was_gas_high = False
                tg_send(
                    f" <b>Gas Level Normal</b>\n"
                    f" Gas: {gas_raw} ({gas_str})\n"
                    f" Relay: OFF - System back to normal."
                )

            lcd.clear()
            lcd.move_to(0, 0)
            lcd.write(f"T:{temp}C H:{humi}%  ")
            lcd.move_to(1, 0)
            lcd.write(f"Gas:{gas_raw} {gas_str}")

    time.sleep_ms(100)

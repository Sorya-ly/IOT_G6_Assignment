from machine import Pin, SPI
from mfrc522 import MFRC522
import network
import urequests
import time
import os

# ─────────────────────────────────────────────
# WiFi
# ─────────────────────────────────────────────
SSID     = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
print("Connecting WiFi", end="")
while not wifi.isconnected():
    print(".", end="")
    time.sleep(0.5)
print("\nConnected:", wifi.ifconfig())

# ─────────────────────────────────────────────
# Firestore
# ─────────────────────────────────────────────
PROJECT_ID    = "lab6-rfid"
COLLECTION    = "attendance"
FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects/{}/databases/(default)/documents/{}".format(
    PROJECT_ID, COLLECTION
)

# ─────────────────────────────────────────────
# Student Database
# ─────────────────────────────────────────────
STUDENTS = {
    "25419520018065": {
        "name":       "Yapheak",
        "student_id": "IDTB100001",
        "major":      "Information Technology"
    },
    # "anotherUID": {"name": "...", "student_id": "...", "major": "..."},
}

# ─────────────────────────────────────────────
# Hardware
# ─────────────────────────────────────────────
buzzer = Pin(4, Pin.OUT)
buzzer.value(0)

# RFID on SPI bus 1
spi = SPI(1, baudrate=1000000,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))
rdr = MFRC522(spi=spi, gpioRst=Pin(22), gpioCs=Pin(16))

# ─────────────────────────────────────────────
# SD Card — CS moved to GPIO 5 (avoid boot pin GPIO 2)
# ─────────────────────────────────────────────
SD_FILE  = "/sd/attendance.csv"
sd_ready = False

def init_sd():
    global sd_ready
    try:
        import sdcard

        # CS pin HIGH before anything else
        sd_cs = Pin(5, Pin.OUT)   # ← changed from GPIO 2 to GPIO 5
        sd_cs.value(1)
        time.sleep_ms(100)

        # SD on SPI bus 2 with lower baudrate for stability
        sd_spi = SPI(2, baudrate=400000,   # ← lowered from 1000000
                     sck=Pin(14), mosi=Pin(13), miso=Pin(15))

        sd = sdcard.SDCard(sd_spi, sd_cs)
        os.mount(sd, "/sd")

        # Write CSV header if file doesn't exist
        try:
            open(SD_FILE, "r").close()
        except:
            with open(SD_FILE, "w") as f:
                f.write("UID,Name,StudentID,Major,DateTime\n")

        print("SD card ready.")
        sd_ready = True

    except Exception as e:
        print("SD init failed:", e)
        print("Continuing without SD logging.")

init_sd()

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def get_datetime():
    try:
        import ntptime
        ntptime.settime()
    except:
        pass
    t = time.localtime()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )

def beep(duration):
    buzzer.value(1)
    time.sleep(duration)
    buzzer.value(0)

def log_to_sd(uid, name, student_id, major, dt):
    if not sd_ready:
        print("SD not available, skipping local log.")
        return
    try:
        with open(SD_FILE, "a") as f:
            f.write("{},{},{},{},{}\n".format(uid, name, student_id, major, dt))
        print("SD logged:", uid)
    except Exception as e:
        print("SD write error:", e)

def send_to_firestore(uid, name, student_id, major, dt):
    data = {
        "fields": {
            "uid":       {"stringValue": uid},
            "name":      {"stringValue": name},
            "studentId": {"stringValue": student_id},
            "major":     {"stringValue": major},
            "dateTime":  {"stringValue": dt},
        }
    }
    try:
        res = urequests.post(FIRESTORE_URL, json=data)
        print("Firestore sent:", res.status_code)
        res.close()
    except Exception as e:
        print("Firestore error:", e)

# ─────────────────────────────────────────────
# Main Loop
# ─────────────────────────────────────────────
print("Scan RFID card...")

while True:
    (stat, tag_type) = rdr.request(rdr.REQIDL)

    if stat == rdr.OK:
        (stat, raw_uid) = rdr.anticoll()

        if stat == rdr.OK:
            uid_str = "".join([str(i) for i in raw_uid])
            print("UID detected:", uid_str)

            student = STUDENTS.get(uid_str)

            if student:
                # Valid card
                dt = get_datetime()
                print("Valid:", student["name"], "|", dt)
                beep(0.3)
                log_to_sd(uid_str, student["name"], student["student_id"], student["major"], dt)
                send_to_firestore(uid_str, student["name"], student["student_id"], student["major"], dt)
            else:
                # Invalid card
                print("Unknown Card")
                beep(3)

            time.sleep(2)


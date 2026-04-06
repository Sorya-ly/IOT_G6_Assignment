from machine import Pin, I2C, PWM
import neopixel
import time
import tcs34725
import network
import socket

# -------------------------------
# WiFi Setup
# -------------------------------
ssid = "Robotic WIFI"
password = "rbtWIFI@2025"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(0.1)

ip = wifi.ifconfig()[0]
print("Connected! IP:", ip)

# -------------------------------
# NeoPixel
# -------------------------------
led = neopixel.NeoPixel(Pin(23), 24)

# -------------------------------
# Color Sensor
# -------------------------------
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = tcs34725.TCS34725(i2c)

# -------------------------------
# Motor (L298N)
# -------------------------------
IN1 = Pin(27, Pin.OUT)
IN2 = Pin(26, Pin.OUT)
ENA = PWM(Pin(14))
ENA.freq(1000)

current_color = "OFF"

# -------------------------------
# LED Function
# -------------------------------
def show_color(color_name):
    if color_name == "RED":
        led.fill((255, 0, 0))
    elif color_name == "GREEN":
        led.fill((0, 255, 0))
    elif color_name == "BLUE":
        led.fill((0, 0, 255))
    else:
        led.fill((0, 0, 0))
    led.write()
    print("Showing:", color_name)

# -------------------------------
# Motor Control
# -------------------------------
def motor_control(color_name):
    if color_name == "RED":
        IN1.value(1)
        IN2.value(0)
        ENA.duty(700)
    elif color_name == "GREEN":
        IN1.value(1)
        IN2.value(0)
        ENA.duty(500)
    elif color_name == "BLUE":
        IN1.value(1)
        IN2.value(0)
        ENA.duty(300)
    else:
        IN1.value(0)
        IN2.value(0)
        ENA.duty(0)

# -------------------------------
# HTTP Response Helper
# -------------------------------
def send_response(conn, body):
    http_response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n{}".format(len(body), body)
    conn.send(http_response)
    conn.close()

# -------------------------------
# Server Setup
# -------------------------------
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(1)
print("Server started at http://{}".format(ip))

# -------------------------------
# Main Loop
# -------------------------------
while True:

    # ✅ Sensor read wrapped in try/except so a crash won't kill the server
    try:
        r, g, b, c = sensor.read_raw()
        print("R:", r, "G:", g, "B:", b, "C:", c)

        if r < 700 and g < 700 and b < 700:
            current_color = "OFF"
        elif r > g and r > b:
            current_color = "RED"
        elif g > r and g > b:
            current_color = "GREEN"
        elif b > r and b > g:
            current_color = "BLUE"
        else:
            current_color = "OFF"

        show_color(current_color)
        motor_control(current_color)

    except Exception as e:
        print("Sensor error:", e)
        # Keep last known color and carry on

    # ---------------------------
    # Handle App Request
    # ---------------------------
    try:
        #server.settimeout(0.1)
        conn, addr = server.accept()
        request = conn.recv(1024).decode()
 
        # Parse only the path from the first line e.g. "GET /color HTTP/1.1"
        first_line = request.split("\r\n")[0]
        parts = first_line.split(" ")
        path = parts[1] if len(parts) > 1 else "/"
        print("Request path:", path)

        if path == "/color":
            print("Sending color:", current_color)
            send_response(conn, current_color)

        elif path == "/forward":
            IN1.value(1)
            IN2.value(0)
            ENA.duty(600)
            send_response(conn, "OK")

        elif path == "/backward":
            IN1.value(0)
            IN2.value(1)
            ENA.duty(600)
            send_response(conn, "OK")

        elif path == "/stop":
            IN1.value(0)
            IN2.value(0)
            ENA.duty(0)
            send_response(conn, "OK")

        elif path.startswith("/setcolor?"):
            try:
                r_val = int(path.split("r=")[1].split("&")[0])
                g_val = int(path.split("g=")[1].split("&")[0])
                b_val = int(path.split("b=")[1].split("&")[0])
                led.fill((r_val, g_val, b_val))
                led.write()
                send_response(conn, "OK")
            except Exception as e:
                print("Setcolor error:", e)
                send_response(conn, "ERROR")

        else:
            print("Unknown path:", path)
            send_response(conn, "INVALID")

    except OSError:
        pass  # Timeout - no request came in, that's fine

    time.sleep(0.2)
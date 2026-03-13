
## ICT 360 001 – Introduction to Internet of Things 

### Project title: Smart IoT Parking Management System 


### Instructor: Theara SENG 

  
### Prepared by Group: 
Ponita PONLORK 
Sophaltheany SEAN 
Soryapheak LY 
 
 
March 9th, 2026 
 


## 1. Introduction

The Smart IoT Parking Management System is a comprehensive embedded systems project designed and implemented on an ESP32 microcontroller using MicroPython. The system addresses a real-world urban challenge: the inefficient use of parking spaces and the lack of real-time information available to drivers and parking administrators.

In modern cities, parking management is a significant logistical problem. Drivers spend valuable time circling parking lots in search of available spaces, contributing to traffic congestion, fuel wastage, and increased emissions. This project proposes an automated, intelligent solution that leverages IoT technologies to monitor parking availability, control entry gates, entry detection and communicate system status across multiple digital platforms.

The system integrates physical sensors and actuators with three distinct IoT platforms — a Telegram Bot, a Web Server Dashboard, and the Blynk mobile application — to provide seamless real-time monitoring and remote-control capabilities. Users and administrators can interact with the system through automated notifications, manual commands, or live dashboards regardless of their physical location.

## 2. Hardware Description

This section describes all hardware components used in the Smart IoT Parking Management System, including their specifications, roles, and connection interfaces.

Component	Role in System
ESP32	Main microcontroller, handles all sensor reads, commends, IoT communication, and display updates concurrently using cooperative multitasking. 
Ultrasonic Sensor	Vehicle entry detection at the parking entry point. 
A threshold distance (typically 20–30 cm) is configured to detect when a vehicle is present at the gate.
The ESP32 triggers the sensor and calculates distance using the formula: Distance = (Time x Speed of Sound) / 2.
IR Sensors (x3)	Parking slot occupancy. Each IR sensor outputs a LOW signal when an object (vehicle) is detected and HIGH when the slot is empty. The ESP32 polls these sensors continuously to maintain an accurate count of occupied versus available slots.
Servo Motor	Gate barrier control. It is controlled via PWM signals from the ESP32. A 0° position represents the closed gate, while a 90° position lifts the barrier to allow entry. The gate automatically closes after a configurable delay once a vehicle has passed through.


DHT11	Environmental monitoring, ambient temperature and relative humidity within the parking structure. 
TM1637 Display	Available slot counter, It is driven via a two-wire CLK/DIO interface and updates in real time whenever a slot state changes.
LCD I2C (16x2)	System status display, It shows scrolling or static information including the gate status, (OPEN/CLOSED), available slot count, temperature readings, and system alerts. 

## 3. System Architecture

The Smart IoT Parking Management System follows a layered IoT architecture comprising four main tiers: the Sensing Layer, the Processing Layer, the Communication Layer, and the Application Layer.

APPLICATION LAYER
Telegram Bot  |  Web Server Dashboard  |  Blynk App
↕  Wi-Fi / HTTP / MQTT
PROCESSING LAYER
ESP32 (MicroPython) — Decision Logic, State Management, Platform Handler
↕  GPIO / PWM / I2C / UART
SENSING & ACTUATION LAYER
HC-SR04  |  IR Sensors  |  DHT11  |  Servo  |  Relay  |  TM1637  |  LCD I2C




## 4. Software Architecture

Process Flow Diagram
<img width="516" height="147" alt="image" src="https://github.com/user-attachments/assets/ba5bbab1-5ee7-4ea9-ae32-bbb22a6cd7c7" />

## 5. IoT Integration

The system integrates three distinct IoT platforms to provide comprehensive monitoring, alerting, and control functionality. Each platform serves a specific user interaction model: command-driven (Telegram), browser-based (Web Server), and mobile app (Blynk).

### 5.1 Telegram Bot Integration
The Telegram Bot is implemented using the Telegram Bot API via HTTP polling. The ESP32 periodically sends a getUpdates request to the Telegram API and processes any incoming messages. Commands are parsed and dispatched to the appropriate system functions.

Implemented Commands
<img width="1268" height="316" alt="image" src="https://github.com/user-attachments/assets/e5a5e0ae-11a7-42fb-af78-99a881d92175" />


### 5.2 Web Server Dashboard
A lightweight HTTP web server runs directly on the ESP32, accessible via the local Wi-Fi network at the device's IP address. The server is implemented using MicroPython's usocket library and serves a single-page HTML/CSS/JavaScript dashboard. 
#### Dashboard Features
•	Live slot availability display with color-coded indicator (green = available, red = full).
•	Real-time temperature and humidity readings from DHT11.
•	Gate status indicator (OPEN / CLOSED) with animated visual.
•	Manual gate open and close buttons with instant feedback.
•	Auto-refresh every 5 seconds using JavaScript fetch() API calls.

### 5.3 Blynk App Dashboard
The Blynk platform provides a customizable mobile dashboard accessible via the Blynk iOS and Android apps. The ESP32 connects to the Blynk cloud server using the Blynk authentication token and communicates via the Blynk protocol over TCP.

#### Blynk Widgets Configured
•	V1 — Value display widget: Available parking slot counter.
•	V2 — Gauge/Value widget: Live temperature reading from DHT11.
•	V4 — Button widget: Manual servo gate open/close toggle.

## 6. Working Process Explanation

### 6.1 Hardware implementation
#### 6.1.1 ESP32 + Ultrasonic Sensor + Servo Motor
The ultrasonic sensor's TRIG pin is connected to ESP32 GPIO 5, and ECHO to GPIO 18. The servo motor signal wire connects to GPIO 13 with PWM enabled at 50 Hz. Power for the servo is drawn from a 5V external supply shared with the sensor VCC, with all grounds tied to a common GND rail.

The distance measurement function uses MicroPython's time.ticks_us() for microsecond-resolution timing. The servo is controlled by varying duty cycle: 1ms pulse = 0° (closed), 2ms pulse = 90° (open). A software debounce of 2 seconds prevents multiple gate triggers from the same vehicle.
#### 6.1.2 IR Sensors + LCD I2C
Each IR sensor's OUT pin connects to a dedicated GPIO input pin (GPIO 34 for Slot 1, GPIO 35 for Slot 2, with additional pins for more slots). The sensors are configured with their onboard potentiometers to detect the presence of a vehicle chassis at the standard parking slot height.

The LCD I2C module connects to the ESP32's I2C bus on GPIO 21 (SDA) and GPIO 22 (SCL). The I2C address is 0x27 (verifiable via I2C scan). The MicroPython I2C library combined with a custom LCD driver handles character encoding and display positioning.

<img width="579" height="135" alt="image" src="https://github.com/user-attachments/assets/4ee4b958-a7d0-4e8a-af53-86b53f8303be" />


#### 6.1.3 TM1637 Display + DHT11
The TM1637 display uses two GPIO pins for its proprietary CLK/DIO protocol (GPIO 14 for CLK, GPIO 27 for DIO). The MicroPython TM1637 library handles all low-level bit-banging. The display brightness is set to maximum (7) for daytime visibility.

The DHT11 data pin connects to GPIO 15. MicroPython's built-in dht module is used to interface with the sensor. The sensor requires a pull-up resistor (4.7kΩ) on the data line for reliable communication.

<img width="579" height="82" alt="image" src="https://github.com/user-attachments/assets/1b9b2db4-472a-4cd1-b2c6-e5235581d5db" />


### 6.2 Software implementation

#### 6.2.1 Web Server
The web server is implemented as a non-blocking socket server using MicroPython's usocket and uselect modules. The server listens on port 80 and handles one request per main loop iteration to avoid blocking sensor operations.

The HTML dashboard is stored as a compressed string in flash memory and served as a complete page response. The page uses embedded CSS for styling and JavaScript's setInterval() function to poll the /api/status endpoint every 5 seconds, updating all displayed values dynamically.

The API endpoint returns a JSON-formatted string built from the current system state dictionary. This includes: gate status, available slots, total slots, relay status, temperature, humidity, and last event timestamp. The lightweight format ensures fast response times even on the ESP32's constrained networking stack.

#### 6.2.2 Telegram Chatbot
The Telegram Bot integration uses the getUpdates long-polling method. The bot token is stored in config.py and included in all API request URLs. The bot maintains a last_update_id variable to track processed messages and avoid reprocessing.

Command handling uses a dictionary-based dispatch pattern: each /command string maps to a handler function. The handler executes the required system action and calls sendMessage with the appropriate response text. All API calls use MicroPython's urequests library with a 10-second timeout.

Proactive notifications are sent by calling the sendMessage API directly from the relevant system event handlers (e.g., from the gate control function or slot update function), ensuring timely alerts without polling delays.

#### 6.2.3 Blynk Dashboard
Blynk connectivity is maintained using a persistent TCP socket connection to the Blynk cloud server (blynk.cloud, port 80). The MicroPython Blynk client library handles the heartbeat ping (every 10 seconds) and virtual pin read/write protocol.

Virtual pin writes (blynk.virtual_write()) are called from within the main loop whenever sensor values change, ensuring dashboard widgets reflect the current system state. The servo control button on V0 uses a Blynk write handler that intercepts the button press event and calls the appropriate gate function.

The Blynk connection is wrapped in a try-except block with automatic reconnection logic. If the connection drops, the system logs the error to the LCD and attempts reconnection every 30 seconds without interrupting other system functions.

## 7. Challenges Faced

The development of this system presented several significant technical and design challenges. This section documents each challenge and the solution approach adopted by the team.

### 7.1 Concurrent Platform Communication
Managing simultaneous communication with three IoT platforms (Telegram, Web Server, Blynk) while maintaining responsive sensor polling was the most demanding challenge. MicroPython does not support true multithreading on the ESP32 in a straightforward manner, so naive blocking calls to any platform would freeze sensor operations.

Solution: The team implemented a time-sliced cooperative scheduler within the main loop. Each platform communication task is given a maximum execution time budget. Telegram polling is limited to one request per loop iteration, the web server handles one connection per cycle, and Blynk uses non-blocking socket operations. Sensor polling is always prioritized in the first portion of each loop cycle.

### 7.2 Wi-Fi Stability and Reconnection
The ESP32's Wi-Fi connection would occasionally drop during extended operation, particularly when the web server was under load. This caused all three platform integrations to fail silently.

Solution: A connectivity watchdog was implemented that checks network status every 60 seconds. If the connection is lost, the system executes a controlled reconnection procedure while continuing to operate local functions (display updates, sensor reads, gate and relay control remain functional in offline mode).


### 7.3 Servo Jitter and Gate Reliability
The SG90 servo motor exhibited jitter when powered from the ESP32's 3.3V pin, causing erratic gate behavior. Additionally, PWM generation in MicroPython produced slightly inconsistent pulse widths.

Solution: The servo was powered from an external 5V regulated supply (sharing only common ground with the ESP32). The PWM duty cycle values were carefully calibrated empirically for the specific servo unit, and a brief disable-PWM-after-reaching-position technique was implemented to eliminate holding current jitter.


## 8. Future Improvements

The current implementation provides a solid and functional proof-of-concept. The following improvements are proposed for future iterations to enhance scalability, user experience, and commercial viability.
### 8.1 Expanded Slot Capacity
The current design supports a small number of IR sensors limited by available GPIO pins. Future versions would use I2C GPIO expander ICs (such as the PCF8574) to support 16 or more parking slots per ESP32, or implement a distributed architecture with multiple ESP32 nodes communicating over MQTT to a central broker.

### 8.2 License Plate Recognition
Integration of a camera module (ESP32-CAM) at the entry point would enable license plate recognition using an edge AI model or cloud OCR API. This would allow for automated vehicle logging, permit verification, and unauthorized entry prevention.

### 8.3 Payment Integration
A parking fee management system could be integrated by tracking entry and exit times per slot and calculating charges. A QR code-based payment system displayed on the LCD at exit would enable contactless payment.

### 8.4 Predictive Analytics
Historical occupancy data logged to a cloud database (Firebase or InfluxDB) would enable machine learning models to predict peak parking times, optimize lighting and ventilation schedules, and provide administrators with actionable usage insights via a dedicated analytics dashboard.

### 8.5 Vehicle Type Detection
Replacing standard IR sensors with ultrasonic arrays or load-cell-equipped parking pads would enable detection and classification of vehicle types (motorcycle, car, truck), allowing differentiated pricing and slot assignment.





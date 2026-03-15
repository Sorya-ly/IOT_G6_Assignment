# Lab 4
## 1. Overview
In this lab, students will design and implement a multi-sensor IoT monitoring system using
ESP32 and MicroPython (Thonny). The system integrates MLX90614 (body temperature),
MQ-5 (gas sensor), BMP280 (room temperature, pressure, altitude), and DS3231 (RTC).
Students must implement edge logic processing before sending data to Node-RED, where it
will be stored in InfluxDB and visualized in Grafana.

## 2. Learning Outcomes (CLO Alignment)
- Integrate multiple I2C and analog sensors with ESP32.
- Implement moving average filtering for noisy sensor signals.
- Create rule-based classification logic at the edge.
- Structure JSON packets for IoT transmission.
- Store time-series data in InfluxDB.
- Design dashboards using Grafana.

## 3. Equipment

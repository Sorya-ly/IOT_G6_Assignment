Smart Kitchen Safety System
Course Information

Course ICT 360 001
Instructor Theara Seng
Semester Spring 2026

Group Members

Sophaltheany Sean
Ponita Ponlork
Soryapheak Ly

Introduction

Kitchen accidents such as gas leaks, unattended cooking, and overheating are common causes of fires and injuries. These incidents often happen due to human negligence or lack of monitoring. This project aims to develop a Smart Kitchen Safety System using IoT technology to automatically detect dangerous situations and respond in real time. The system combines gas detection, temperature monitoring, and human presence detection to make intelligent decisions that help prevent accidents.

Objectives

Detect gas leaks in real time
Monitor kitchen temperature and identify fire risks
Detect whether a person is present in the kitchen
Automatically respond to dangerous situations
Send alerts to users via Telegram

System Overview

The system is built using two main controllers. The ESP32 CAM handles person detection. The ESP32 Development Board handles sensors and decision making.

System flow
Sensors collect data from gas and temperature
ESP32 CAM detects human presence
ESP32 processes all inputs
System decides the response
Output devices are activated
Alerts are sent via Telegram

Hardware Components

ESP32 CAM
ESP32 Development Board
Gas Sensor MQ 2
Temperature Sensor BME280
Relay Module
Buzzer
RGB LED
Servo Motor for gas valve control
SD Card for data logging

System Architecture

[ESP32 CAM] to Person Detection to [ESP32]
Gas and Temperature Sensors to Logic System
Relay Buzzer Fan and LED from Response
Telegram Bot receives alerts

System Operation

System boot
ESP32 CAM connects to WiFi and starts camera detection
ESP32 initializes sensors and output devices
System sends message Kitchen Safety System ON

Temperature monitoring
Temperature is read every 5 to 10 seconds
If temperature is greater than 40 degrees Celsius a warning alert is triggered
Otherwise the system remains normal

Gas detection
Gas sensor is checked every second
Low gas means normal operation
High gas means gas leak detected

Person detection
ESP32 CAM continuously scans the environment
Output is person yes or person no

Decision logic
Gas detected and no person
Activate alarm using buzzer
Turn off gas supply using relay
Turn on ventilation fan
Send emergency Telegram alert

Gas detected and person present
Activate warning buzzer
Send warning notification
Do not shut system

Features

Real time monitoring
Automatic emergency response
Smart decision making
Remote alert system via Telegram
Expandable design

Expected Outcomes

Reduced risk of kitchen fires and gas accidents
Increased user awareness and safety
Faster response to emergencies
Working IoT based safety prototype

Conclusion

This project demonstrates how IoT technology can improve everyday safety. By combining sensors automation and intelligent logic the Smart Kitchen Safety System provides an effective solution to prevent accidents and protect users.
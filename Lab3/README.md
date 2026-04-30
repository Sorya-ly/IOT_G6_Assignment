# LAB 3
IoT Smart Gate Control with Blynk, IR Sensor, Servo Motor,
and TM1637
## 1. Overview
In this lab, students will design and implement an ESP32-based IoT system using MicroPython
and the Blynk platform. The system integrates an IR sensor for object detection, a servo motor for
physical actuation, and a TM1637 7-segment display for real-time local feedback. Students will
use the Blynk mobile application to remotely control the system, monitor sensor status, and
observe system behavior.
This lab emphasizes interaction between sensors, actuators, cloud-based control, and local
display, reinforcing event-driven and IoT system design concepts.
## 2. Learning Outcomes (CLO Alignment)
• Integrate multiple sensors and actuators into a single IoT system using ESP32.
• Use Blynk to remotely control hardware and visualize system status.
• Implement automatic and manual control logic based on sensor input and cloud commands.
• Display system status and numerical data using a TM1637 7-segment display.
• Document system wiring, logic flow, and IoT behavior clearly.
## 3. Equipment
![Lab 3 Wiring](Lab3/Lab3_wiringPhoto.jpg)
## 4. System Description
The IR sensor detects the presence of an object in front of the system. When an object is detected,
the ESP32 processes the signal and automatically rotates the servo motor to simulate opening a
gate or barrier. Each detection event increments a counter, which is displayed locally on the
TM1637 display and sent to the Blynk app for remote monitoring.
Users can also manually control the servo motor through the Blynk app, overriding the automatic
mode if required.
## 5. Tasks & Checkpoints
All submitted work must be original. Plagiarism or code sharing is strictly prohibited.
### Task 1 – IR Sensor Reading
• Read IR sensor digital output using ESP32.
• Display IR status (Detected / Not Detected) on Blynk.
• Evidence: Screenshot of Blynk showing IR status.
### Task 2 – Servo Motor Control via Blynk
• Add a Blynk Slider widget to control servo position.
• Slider position from 0 to 180 degree and the servo is moving following the slider
• Evidence: Short video showing phone control servo movement.
### Task 3 – Automatic IR - Servo Action
• When IR sensor detects an object, servo opens automatically.
• After a short delay, servo returns to closed position.
• Evidence: Video showing automatic response to object detection.
### Task 4 – TM1637 Display Integration
• Count the number of IR detection events.
• Display the counter value on the TM1637 display.
• Send the same value to Blynk numeric display widget.
• Evidence: Video showing TM1637 display and Blynk value match.
### Task 5 – Manual Override Mode
• Add a Blynk switch to enable/disable automatic IR mode.
• When manual mode is active, IR sensor is ignored.
• Evidence: Demonstration video of override behavior.
## 6. Short demo video
Link: https://youtu.be/YFpb0ajkO_I



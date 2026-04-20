### System Description
The ESP32 continuously reads RGB values from the TCS34725 sensor. Based on the
detected color, the system performs the following:
1. Read RGB values from sensor.
2. Classify detected color (RED, GREEN, BLUE).
3. Control NeoPixel color based on classification.
4. Adjust motor speed using PWM.
5. Send detected color to MIT App.
6. Allow manual override from MIT App (motor + NeoPixel).
### Tasks & Checkpoints
Task 1 - RGB Reading
- Read RGB values from TCS34725.
- Print values to Serial Monitor.
Evidence: Screenshot showing RGB values.

Task 2 - Color Classification
Classification Rules:
- R > G and R > B → RED
- G > R and G > B → GREEN
- B > R and B > G → BLUE
Evidence: Demonstration of correct color detection.

Task 3 - NeoPixel Control
- RED → NeoPixel shows Red
- GREEN → NeoPixel shows Green
- BLUE → NeoPixel shows Blue
Evidence: NeoPixel color change demonstration.

Task 4 - Motor Control (PWM)
- RED → PWM = 700
- GREEN → PWM = 500
- BLUE → PWM = 300
Evidence: Motor speed variation.

Task 5 - MIT App Integration
App Requirements:
- Display detected color (Label).
- Buttons: Forward, Stop, Backward.
- RGB input boxes (R, G, B).
- Button to set NeoPixel color manually.
Evidence: Screenshot of working app.

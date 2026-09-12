# CNC Plotter Hardware Connections

This document details the complete hardware wiring between the Arduino Uno Q, the breadboard, the stepper motor drivers, and the power supply.

## 1. Breadboard & Power Supply Connections
> [!WARNING]
> Never power the stepper motors directly from the Arduino Uno Q's 5V pin! They draw too much current and will damage the board.

* **External Power Supply (+):** Connect to the positive (red) rail on the breadboard. (Use the correct voltage for your motors, typically 5V or 12V).
* **External Power Supply (- / GND):** Connect to the negative (blue/black) rail on the breadboard.
* **Arduino Uno Q GND:** Connect a wire from any `GND` pin on the Arduino Uno Q to the negative (blue/black) rail on the breadboard. **This common ground is critical.**

## 2. Stepper Motor Drivers (e.g., ULN2003)
Each of the 3 motors requires its own driver board. 

### Powering the Drivers:
For **all three** drivers (X, Y, and Z):
* Connect the **`+` or `VCC`** pin on the driver to the positive rail on the breadboard.
* Connect the **`-` or `GND`** pin on the driver to the negative rail on the breadboard.

### Plugging in the Motors:
* Plug the white plastic connector coming from the X-Axis stepper motor directly into the white socket on the X-Axis driver board.
* Plug the Y-Axis stepper motor into the Y-Axis driver board socket.
* Plug the Z-Axis stepper motor into the Z-Axis driver board socket.

---

## 3. Arduino Data Connections (IN1, IN2, IN3, IN4)

Connect the logic pins from the Arduino Uno Q to the inputs on each respective driver board:

### X-Axis Motor Driver (Stepper 1)
* **IN1** $\rightarrow$ Arduino Pin `2`
* **IN2** $\rightarrow$ Arduino Pin `3`
* **IN3** $\rightarrow$ Arduino Pin `4`
* **IN4** $\rightarrow$ Arduino Pin `5`

### Y-Axis Motor Driver (Stepper 2)
* **IN1** $\rightarrow$ Arduino Pin `6`
* **IN2** $\rightarrow$ Arduino Pin `7`
* **IN3** $\rightarrow$ Arduino Pin `8`
* **IN4** $\rightarrow$ Arduino Pin `9`

### Z-Axis Motor Driver (Stepper 3)
* **IN1** $\rightarrow$ Arduino Pin `10`
* **IN2** $\rightarrow$ Arduino Pin `11`
* **IN3** $\rightarrow$ Arduino Pin `12`
* **IN4** $\rightarrow$ Arduino Pin `13`

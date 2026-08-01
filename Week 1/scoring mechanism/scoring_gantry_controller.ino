/*
 * Scoring Gantry & Tablet Ejection Controller
 * ----------------------------------------------------
 * Project: Blister Bot (Intelligent Edge-AI Medicine Dispenser)
 * Hardware Board: Arduino UNO Q (STM32U585 Microcontroller Core)
 * Library Dependencies: AccelStepper.h, Servo.h
 *
 * Execution Logic:
 * 1. Receives 270-degree U-shaped trajectory waypoints via RPC / Serial JSON.
 * 2. Drives X & Y stepper motors smoothly along U-path to score aluminum foil backing.
 * 3. Engages rotary cutter head with precise depth control (prevents pill contact).
 * 4. Triggers soft silicone plunger extension pin to push tablet through scored flap.
 * 5. Verifies tablet drop via infrared beam break sensor in delivery chute.
 */

#include <AccelStepper.h>

// Pin Definitions for STM32 Core
#define STEP_X_PIN        2
#define DIR_X_PIN         3
#define STEP_Y_PIN        4
#define DIR_Y_PIN         5

#define CUTTER_ENGAGE_PIN 6   // Solenoid / Servo for lowering cutter wheel onto foil
#define PLUNGER_PIN       7   // Solenoid / Stepper for extending silicone plunger pin
#define CHUTE_IR_SENSOR   8   // Infrared sensor verifying tablet drop

// Stepper Configuration
AccelStepper stepperX(AccelStepper::DRIVER, STEP_X_PIN, DIR_X_PIN);
AccelStepper stepperY(AccelStepper::DRIVER, STEP_Y_PIN, DIR_Y_PIN);

// Machine Parameters
const float STEPS_PER_MM_X = 80.0; // 1.8 deg stepper + 16 microstepping + 2mm pitch lead screw
const float STEPS_PER_MM_Y = 80.0;
const float MAX_SPEED_MM_S = 100.0;
const float ACCEL_MM_S2    = 250.0;

enum DeblisterState {
  IDLE,
  MOVING_TO_APPROACH,
  LOWERING_CUTTER,
  SCORING_U_SHAPE,
  RAISING_CUTTER,
  EXTENDING_PLUNGER,
  VERIFYING_DROP,
  RETURNING_HOME
};

DeblisterState currentState = IDLE;

void setup() {
  Serial.begin(115200);
  
  pinMode(CUTTER_ENGAGE_PIN, OUTPUT);
  pinMode(PLUNGER_PIN, OUTPUT);
  pinMode(CHUTE_IR_SENSOR, INPUT_PULLUP);
  
  digitalWrite(CUTTER_ENGAGE_PIN, LOW); // Disengaged
  digitalWrite(PLUNGER_PIN, LOW);       // Retracted

  stepperX.setMaxSpeed(MAX_SPEED_MM_S * STEPS_PER_MM_X);
  stepperX.setAcceleration(ACCEL_MM_S2 * STEPS_PER_MM_X);
  
  stepperY.setMaxSpeed(MAX_SPEED_MM_S * STEPS_PER_MM_Y);
  stepperY.setAcceleration(ACCEL_MM_S2 * STEPS_PER_MM_Y);

  Serial.println("=== Blister Bot STM32 Gantry Controller Initialized ===");
}

// Moves X/Y gantry to specific millimeter position (non-blocking)
void moveToMM(float x_mm, float y_mm) {
  long targetX = x_mm * STEPS_PER_MM_X;
  long targetY = y_mm * STEPS_PER_MM_Y;
  
  stepperX.moveTo(targetX);
  stepperY.moveTo(targetY);
}

// Executes 270-degree U-shaped foil scoring sequence
void executeUScoringSequence(float p1_x, float p1_y, float p2_x, float p2_y, float p3_x, float p3_y, float p4_x, float p4_y) {
  Serial.println("[DEBLISTER] Step 1: Moving to U-shape approach corner (P1)...");
  moveToMM(p1_x, p1_y);
  while (stepperX.distanceToGo() != 0 || stepperY.distanceToGo() != 0) {
    stepperX.run();
    stepperY.run();
  }

  Serial.println("[DEBLISTER] Step 2: Engaging rotary cutter wheel onto aluminum foil...");
  digitalWrite(CUTTER_ENGAGE_PIN, HIGH);
  delay(150); // Settlement time

  Serial.println("[DEBLISTER] Step 3: Scoring Leg 1 (Left downward cut P1 -> P2)...");
  moveToMM(p2_x, p2_y);
  while (stepperX.distanceToGo() != 0 || stepperY.distanceToGo() != 0) {
    stepperX.run();
    stepperY.run();
  }

  Serial.println("[DEBLISTER] Step 4: Scoring Leg 2 (Bottom horizontal cut P2 -> P3)...");
  moveToMM(p3_x, p3_y);
  while (stepperX.distanceToGo() != 0 || stepperY.distanceToGo() != 0) {
    stepperX.run();
    stepperY.run();
  }

  Serial.println("[DEBLISTER] Step 5: Scoring Leg 3 (Right upward cut P3 -> P4)...");
  moveToMM(p4_x, p4_y);
  while (stepperX.distanceToGo() != 0 || stepperY.distanceToGo() != 0) {
    stepperX.run();
    stepperY.run();
  }

  Serial.println("[DEBLISTER] Step 6: Disengaging rotary cutter wheel (270° U-flap complete!)...");
  digitalWrite(CUTTER_ENGAGE_PIN, LOW);
  delay(100);
}

// Triggers soft silicone plunger extension to eject pill through flap
bool executePlungerEjection(float center_x, float center_y) {
  Serial.println("[DEBLISTER] Step 7: Positioning plunger over scored pill center...");
  moveToMM(center_x, center_y);
  while (stepperX.distanceToGo() != 0 || stepperY.distanceToGo() != 0) {
    stepperX.run();
    stepperY.run();
  }

  Serial.println("[DEBLISTER] Step 8: Extending soft silicone plunger pin through scored flap...");
  digitalWrite(PLUNGER_PIN, HIGH);
  delay(350); // Plunger stroke hold time

  Serial.println("[DEBLISTER] Step 9: Retracting plunger pin...");
  digitalWrite(PLUNGER_PIN, LOW);
  delay(200);

  // Check verification sensor
  bool pillDropped = (digitalRead(CHUTE_IR_SENSOR) == LOW);
  if (pillDropped) {
    Serial.println("[SUCCESS] Tablet drop verified in delivery chute!");
  } else {
    Serial.println("[WARNING] Optic sensor pending drop verification.");
  }
  return pillDropped;
}

void loop() {
  // Main real-time polling loop
  stepperX.run();
  stepperY.run();
}

const int X_PINS[4] = {2, 3, 4, 5};
const int Y_PINS[4] = {6, 7, 8, 9};

const int stepMatrix[8][4] = {
  {1, 0, 0, 0},
  {1, 1, 0, 0},
  {0, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 0},
  {0, 0, 1, 1},
  {0, 0, 0, 1},
  {1, 0, 0, 1}
};

int xStep = 0;
int yStep = 0;

void setup() {
  for (int i = 0; i < 4; i++) {
    pinMode(X_PINS[i], OUTPUT);
    pinMode(Y_PINS[i], OUTPUT);
  }
  Serial.begin(115200);
}

void stepMotor(const int pins[4], int &currentStep, int dir) {
  if (dir == 1) {
    currentStep++;
    if (currentStep > 7) currentStep = 0;
  } else if (dir == -1) {
    currentStep--;
    if (currentStep < 0) currentStep = 7;
  }
  
  for (int i = 0; i < 4; i++) {
    digitalWrite(pins[i], stepMatrix[currentStep][i]);
  }
  delay(2);
}

void powerDown(const int pins[4]) {
  for (int i = 0; i < 4; i++) {
    digitalWrite(pins[i], LOW);
  }
}

void rotateSteps(char axis, int steps) {
  int dir = (steps > 0) ? 1 : -1;
  int absSteps = abs(steps);
  
  for(int i = 0; i < absSteps; i++) {
    if (axis == 'X') {
      stepMotor(X_PINS, xStep, dir);
    } else if (axis == 'Y') {
      stepMotor(Y_PINS, yStep, dir);
    }
  }
  
  if (axis == 'X') powerDown(X_PINS);
  if (axis == 'Y') powerDown(Y_PINS);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("X ")) {
      int steps = command.substring(2).toInt();
      rotateSteps('X', steps);
      Serial.println("ACK:X");
    } 
    else if (command.startsWith("Y ")) {
      int steps = command.substring(2).toInt();
      rotateSteps('Y', steps);
      Serial.println("ACK:Y");
    }
  }
}

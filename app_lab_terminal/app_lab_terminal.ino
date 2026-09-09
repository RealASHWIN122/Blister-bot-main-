#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"

Arduino_LED_Matrix matrix;
String currentMessage = "  Waiting for AI...  ";

void setup() {
  Serial1.begin(115200);
  matrix.begin();
  matrix.textFont(Font_5x7);
  matrix.textScrollSpeed(80);
}

void loop() {
  if (Serial1.available() > 0) {
    String command = Serial1.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("PRINT:")) {
      currentMessage = "  " + command.substring(6) + "  ";
    }
  }

  matrix.clear();
  matrix.beginText(0, 0, 127, 0, 0);
  matrix.print(currentMessage);
  matrix.endText(SCROLL_LEFT);
}

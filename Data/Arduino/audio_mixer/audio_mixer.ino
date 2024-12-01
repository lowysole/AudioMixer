const int NUM_SLIDERS = 5;
const int analogInputs[NUM_SLIDERS] = { A0, A1, A2, A3, A4 };
const int NUM_BUTTONS = 4;
const int digitalInputs[NUM_BUTTONS] = { 9, 10, 11, 12 };
const int digitalOutputs[NUM_BUTTONS] = { 5, 6, 7, 8 };

int analogSliderValues[NUM_SLIDERS];

void setup() {
  for (int i = 0; i < NUM_SLIDERS; ++i) {
    pinMode(analogInputs[i], INPUT);
  }

  for (int i = 0; i < NUM_BUTTONS; ++i) {
    pinMode(digitalInputs[i], INPUT);
    pinMode(digitalOutputs[i], OUTPUT);
  }

  Serial.begin(9600);
}

void loop() {
  updateSliderValues();
  updateButtonValues();
  sendSliderValues();
  //printSliderValues(); // For debug
  delay(10);
}

void updateSliderValues() {
  for (int i = 0; i < NUM_SLIDERS; i++) {
    analogSliderValues[i] = analogRead(analogInputs[i]);
  }
}

void updateButtonValues() {
  for (int i = 0; i < NUM_BUTTONS; i++) {

    Serial.println(digitalRead(digitalInputs[0]));
    digitalWrite(digitalOutputs[i], !digitalRead(digitalInputs[i]));
  }
}


void sendSliderValues() {
  String builtString = String("");

  for (int i = 0; i < NUM_SLIDERS; i++) {
    builtString += String((int)analogSliderValues[i]);

    if (i < NUM_SLIDERS - 1) {
      builtString += String("|");
    }
  }
  
  Serial.println(builtString.c_str());
}

void printSliderValues() {
  for (int i = 0; i < NUM_SLIDERS; i++) {
    String printedString = String("Slider #") + String(i + 1) + String(": ") + String(analogSliderValues[i]) + String(" mV");
    Serial.write(printedString.c_str());

    if (i < NUM_SLIDERS - 1) {
      Serial.write(" | ");
    } else {
      Serial.write("\n");
    }
  }

  delay(500);
}

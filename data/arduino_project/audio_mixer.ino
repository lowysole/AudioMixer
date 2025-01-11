#include <U8g2lib.h>
#include <Wire.h>

const int NUM_SLIDERS = 5;
const int analogInputs[NUM_SLIDERS] = { A0, A1, A2, A3, A7 };
const int NUM_BUTTONS = 4;
const int digitalInputs[NUM_BUTTONS] = { 2, 3, 4, 5 };
const int digitalOutputs[NUM_BUTTONS] = { 7, 8, 9, 10 };

U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/U8X8_PIN_NONE);

void setup() {

  setupDisplay();

  for (int i = 0; i < NUM_SLIDERS; ++i) {
    pinMode(analogInputs[i], INPUT);
  }

  for (int i = 0; i < NUM_BUTTONS; ++i) {
    pinMode(digitalInputs[i], INPUT_PULLUP);
    pinMode(digitalOutputs[i], OUTPUT);
  }

  Serial.begin(57600);
}

void loop() {

  sendOutputValues();

  delay(100);
}


void setupDisplay() {
  u8g2.begin();
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.drawStr(0, 24, "Hello, U8g2!");
  u8g2.sendBuffer();
}

int updateSliderValues(int slider) {
  // Invert values from main slider (knob)
  if (slider == NUM_SLIDERS - 1) {
    return (1023 - analogRead(analogInputs[NUM_SLIDERS - 1])) * 0.09765625; // 100/1024
  } else if (slider < NUM_SLIDERS - 1) {
    return analogRead(analogInputs[slider]) * 0.09765625;
  }

  return 0;
}
bool buttonState = HIGH;  // Estado del botón (inicialmente no presionado)
unsigned long lastPressTime = 0; // Tiempo de la última pulsación
const unsigned long debounceDelay = 50; // Tiempo de debounce en ms

bool updateButtonValues(int button) {
  bool inputState = !digitalRead(digitalInputs[button]);
  digitalWrite(digitalOutputs[button], inputState);
  return inputState;
}


void sendOutputValues() {
  String builtString = String("");

  // SLIDERS
  for (int i = 0; i < NUM_SLIDERS; i++) {
    builtString += String((int)updateSliderValues(i));

    if (i < NUM_SLIDERS) {
      builtString += String("|");
    }
  }

  // BUTTONS
  for (int i = 0; i < NUM_BUTTONS; i++) {
    builtString += String((bool)updateButtonValues(i));

    if (i < NUM_BUTTONS - 1) {
      builtString += String("|");
    }
  }

  Serial.println(builtString.c_str());
}

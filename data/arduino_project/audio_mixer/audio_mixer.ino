#include <U8g2lib.h>
#include <Wire.h>

const char* DELIMITER = "|";
const int NUM_SLIDERS = 5;
const int analogInputs[NUM_SLIDERS] = {A7, A0, A1, A2, A3};
const int NUM_BUTTONS = 4;
const int digitalInputs[NUM_BUTTONS] = {2, 3, 4, 5};
const int digitalOutputs[NUM_BUTTONS] = {7, 8, 9, 10};

bool buttonMode[NUM_BUTTONS] = {0, 0, 0, 0};  // 0: PUSH, 1: TOOGLE
bool previousButtonState[NUM_BUTTONS] = {false, false, false, false};
bool previousLEDState[NUM_BUTTONS] = {false, false, false, false};

U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/U8X8_PIN_NONE);

String readLine()
{
    String input = "";
    while (Serial.available() > 0)
    {
        char c = Serial.read();  // Read the next character
        if (c == '\n')
        {
            break;  // Stop reading at the newline character
        }
        input += c;  // Append the character to the string
    }
    return input;
}

void setup()
{
    setupDisplay(1);

    for (int i = 0; i < NUM_SLIDERS; ++i)
    {
        pinMode(analogInputs[i], INPUT);
    }

    for (int i = 0; i < NUM_BUTTONS; ++i)
    {
        pinMode(digitalInputs[i], INPUT_PULLUP);
        pinMode(digitalOutputs[i], OUTPUT);
    }

    Serial.begin(9600);
}

void loop()
{
    readInputValues();
    sendOutputValues();
    delay(100);
}

void setupDisplay(int preset)
{
    u8g2.begin();
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_helvB12_tr);
    u8g2.drawStr(5, 24, "AUDIO DECK");

    char presetName[25];
    sprintf(presetName, "Preset: %d", preset);
    u8g2.drawStr(5, 48, presetName);
    u8g2.sendBuffer();
}

void readInputValues()
{
    if (Serial.available() > 0)
    {
        String data = readLine();

        char* action = strtok(data.c_str(), DELIMITER);
        if (!strcmp(action, "BUTTON_MODE"))
        {
            for (int i = 0; i < NUM_BUTTONS; ++i)
            {
                buttonMode[i] = atoi(strtok(NULL, DELIMITER));
            }
        }
        else if (!strcmp(action, "BUTTON_INIT"))
        {
            for (int i = 0; i < NUM_BUTTONS; ++i)
            {
                previousLEDState[i] = atoi(strtok(NULL, DELIMITER));
                digitalWrite(digitalOutputs[i], previousLEDState[i]);
            }
        }
        else if (!strcmp(action, "PRESET"))
        {
            setupDisplay(atoi(strtok(NULL, DELIMITER)));
        }
    }
}

int updateSliderValues(int slider)
{
    if (slider == 0)  // Invert values from main slider (knob)
    {
        return (1023 - analogRead(analogInputs[0])) * 0.09765625;  // 100/1024
    }
    else if (slider < NUM_SLIDERS)
    {
        return analogRead(analogInputs[slider]) * 0.09765625;
    }

    return 0;
}

bool updateButtonValues(int button)
{
    if (buttonMode[button])
    {
        bool inputState = digitalRead(digitalInputs[button]);
        if (previousButtonState[button] && !inputState)
        {
            previousLEDState[button] = !previousLEDState[button];
            digitalWrite(digitalOutputs[button], previousLEDState[button]);
        }
        previousButtonState[button] = inputState;
        return previousLEDState[button];
    }
    else
    {
        bool inputState = !digitalRead(digitalInputs[button]);
        digitalWrite(digitalOutputs[button], inputState);
        return inputState;
    }
}

void sendOutputValues()
{
    char builtString[100];
    int index = 0;

    // SLIDERS
    for (int i = 0; i < NUM_SLIDERS; i++)
    {
        index += sprintf(&builtString[index], "%d", updateSliderValues(i));

        if (i < NUM_SLIDERS)
        {
            index += sprintf(&builtString[index], "%s", DELIMITER);
        }
    }

    // BUTTONS
    for (int i = 0; i < NUM_BUTTONS; i++)
    {
        index += sprintf(&builtString[index], "%d", updateButtonValues(i));

        if (i < NUM_BUTTONS - 1)
        {
            index += sprintf(&builtString[index], "%s", DELIMITER);
        }
    }

    sprintf(&builtString[index], "\n");
    Serial.print(builtString);
}

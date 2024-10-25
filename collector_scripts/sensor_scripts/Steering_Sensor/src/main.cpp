/*#include <Arduino.h>

#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

#define A_PHASE 21
#define B_PHASE 22

volatile int position = 0;  // Track the relative position of the encoder
unsigned int flagA = 0;  // Counter for CCW (Counter-Clockwise) direction
unsigned int flagB = 0;  // Counter for CW (Clockwise) direction
const float pulses_per_rev = 600.0;  // Encoder specification (600 P/R)
const float degrees_per_pulse = 360.0 / pulses_per_rev;  // 0.6 degrees per pulse

const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";
unsigned int localUdpPort = 8778;
float angle = 0;

WiFiUDP udp;

void IRAM_ATTR interruptA() {  // Interrupt on A-phase (Pin 21)
  if (digitalRead(B_PHASE) == HIGH) {  // B-phase is HIGH, meaning CW
    position++;
    flagB++;
  } else {  // B-phase is LOW, meaning CCW
    position--;
    flagA++;
  }
}

void setup() {

  pinMode(A_PHASE, INPUT);
  pinMode(B_PHASE, INPUT);

  Serial.begin(115200);   // Serial Port Baudrate

  attachInterrupt(digitalPinToInterrupt(A_PHASE), interruptA, RISING);  // Interrupt trigger on rising edge of A-phase

  WiFi.hostname("Steering_ESP");
	WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
	{
		delay(1000); // setting sending rate
		Serial.println("Connecting with WiFi");
	}

  udp.begin(localUdpPort);
}

void loop() {

  StaticJsonDocument<500> doc;
  int packetSize = udp.parsePacket();

  // Calculate the absolute angle

  float newAngle = (position * degrees_per_pulse);
  if (newAngle - angle < 1.0 || newAngle - angle > 1.0) {
    angle = newAngle;
  }
  
  String jsonStr;
	doc["sensor"] = "BNO055";
	doc["euler_h"] = angle;

  
	serializeJson(doc, jsonStr);

	udp.beginPacket("192.168.0.101", localUdpPort);
	udp.print(jsonStr);
	udp.endPacket();

  Serial.print("Absolute Angle: ");
  Serial.println(angle);
  
  delay(50);  // Short delay to avoid flooding the serial output
}*/

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

#define A_PHASE 21
#define B_PHASE 22

volatile int position = 0;  // Track the relative position of the encoder
unsigned int flagA = 0;  // Counter for CCW (Counter-Clockwise) direction
unsigned int flagB = 0;  // Counter for CW (Clockwise) direction
const float pulses_per_rev = 600.0;  // Encoder specification (600 P/R)
const float degrees_per_pulse = 360.0 / (pulses_per_rev * 4);  // Quadrature decoding gives 4x the resolution

const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";
unsigned int localUdpPort = 8778;
float angle = 0;

WiFiUDP udp;

// State tracking for quadrature decoding
volatile int lastAState = 0;
volatile int lastBState = 0;

// Minimum change in degrees to update
const float hysteresisThreshold = 1.2;
float lastAngle = 0.0;  // Last reported angle

// Variables for non-blocking timing
unsigned long previousMillis = 0;
const unsigned long interval = 50;  // Send data every 50ms

// Quadrature decoding ISR
void IRAM_ATTR updateEncoder() {
  int AState = digitalRead(A_PHASE);  // Current state of A phase
  int BState = digitalRead(B_PHASE);  // Current state of B phase
  
  // Determine direction based on the state changes
  if (AState != lastAState) {  // A phase changed
    if (AState == BState) {
      position++;  // Clockwise
      flagB++;
    } else {
      position--;  // Counterclockwise
      flagA++;
    }
  } else if (BState != lastBState) {  // B phase changed
    if (AState != BState) {
      position++;  // Clockwise
      flagB++;
    } else {
      position--;  // Counterclockwise
      flagA++;
    }
  }
  
  lastAState = AState;
  lastBState = BState;
}

void setup() {
  pinMode(A_PHASE, INPUT);
  pinMode(B_PHASE, INPUT);

  // Read initial states
  lastAState = digitalRead(A_PHASE);
  lastBState = digitalRead(B_PHASE);

  Serial.begin(115200);   // Serial Port Baudrate

  // Attach interrupts for both A and B phases
  attachInterrupt(digitalPinToInterrupt(A_PHASE), updateEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(B_PHASE), updateEncoder, CHANGE);

  WiFi.hostname("Steering_ESP");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000); // setting sending rate
    Serial.println("Connecting with WiFi");
  }

  udp.begin(localUdpPort);
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Only send data if 50 ms have passed
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Calculate the absolute angle based on the current position
    float newAngle = (position * degrees_per_pulse);

    // Apply hysteresis filter: only update the angle if the change exceeds the threshold
    if (abs(newAngle - lastAngle) >= hysteresisThreshold) {
      angle = newAngle;
      lastAngle = newAngle;
    }
    //angle = newAngle;

    // Prepare JSON data to send over UDP
    StaticJsonDocument<500> doc;
    String jsonStr;
    doc["sensor"] = "BNO055";
    doc["euler_h"] = angle;

    serializeJson(doc, jsonStr);

    // Send the JSON packet over UDP
    udp.beginPacket("192.168.0.101", localUdpPort);
    udp.print(jsonStr);
    udp.endPacket();

    // Print the current angle to the Serial Monitor
    Serial.print("Absolute Angle: ");
    Serial.println(angle);
  }
}

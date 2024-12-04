#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

#define A_PHASE 21
#define B_PHASE 22

// Variables for tracking the relative position of the encoder
volatile int position = 0;  // Encoder position
unsigned int flagA = 0;  // Counter for Counter-Clockwise (CCW) direction
unsigned int flagB = 0;  // Counter for Clockwise (CW) direction

// Encoder specifications and derived calculations
const float pulses_per_rev = 600.0;  // Encoder pulses per revolution (600 P/R)
const float degrees_per_pulse = 360.0 / (pulses_per_rev * 4);  // Quadrature decoding increases resolution by 4x

// Wi-Fi credentials for connecting to the VR setup network
const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";

// UDP configuration
unsigned int localUdpPort = 8778;  // Local UDP port for sending data
float angle = 0;  // Current calculated steering angle

WiFiUDP udp;

// Variables for tracking the encoder's quadrature decoding state
volatile int lastAState = 0;
volatile int lastBState = 0;

// Hysteresis filter threshold and timing configuration
const float hysteresisThreshold = 1.2;  // Minimum change in degrees to update
float lastAngle = 0.0;  // Last reported angle to avoid unnecessary updates
unsigned long previousMillis = 0;
const unsigned long interval = 50;  // Interval (ms) for sending updates over UDP

// Interrupt Service Routine (ISR) for handling encoder quadrature decoding
void IRAM_ATTR updateEncoder() {
  int AState = digitalRead(A_PHASE);  // Read current state of A phase
  int BState = digitalRead(B_PHASE);  // Read current state of B phase
  
  // Determine rotation direction based on quadrature signal changes
  if (AState != lastAState) {  // A phase state has changed
    if (AState == BState) {
      position++;  // Clockwise (CW) rotation
      flagB++;
    } else {
      position--;  // Counter-Clockwise (CCW) rotation
      flagA++;
    }
  } else if (BState != lastBState) {  // B phase state has changed
    if (AState != BState) {
      position++;  // Clockwise (CW) rotation
      flagB++;
    } else {
      position--;  // Counter-Clockwise (CCW) rotation
      flagA++;
    }
  }

  // Update last known states
  lastAState = AState;
  lastBState = BState;
}

void setup() {
  // Configure encoder input pins
  pinMode(A_PHASE, INPUT);
  pinMode(B_PHASE, INPUT);

  // Initialize encoder states
  lastAState = digitalRead(A_PHASE);
  lastBState = digitalRead(B_PHASE);

  // Initialize serial communication for debugging
  Serial.begin(115200);

  // Attach interrupts for encoder quadrature decoding
  attachInterrupt(digitalPinToInterrupt(A_PHASE), updateEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(B_PHASE), updateEncoder, CHANGE);

  // Connect to the VR setup's Wi-Fi network
  WiFi.hostname("Steering_ESP");
  WiFi.begin(ssid, password);

  // Wait for the Wi-Fi connection to be established
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);  // Retry connection every second
    Serial.println("Connecting with WiFi");
  }

  // Start the UDP service
  udp.begin(localUdpPort);
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Send data at regular intervals
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Calculate the absolute steering angle from the encoder position
    float newAngle = (position * degrees_per_pulse);

    // Apply hysteresis filtering to reduce noise in updates
    if (abs(newAngle - lastAngle) >= hysteresisThreshold) {
      angle = newAngle;
      lastAngle = newAngle;
    }

    // Prepare JSON data containing the steering angle
    StaticJsonDocument<500> doc;
    String jsonStr;
    doc["sensor"] = "PHOTO_INCREMENT";  // Identifier for the steering sensor
    doc["angle"] = angle;  // Steering angle in degrees

    serializeJson(doc, jsonStr);

    // Send the JSON data to the main VR PC via UDP
    udp.beginPacket("192.168.0.101", localUdpPort);
    udp.print(jsonStr);
    udp.endPacket();

    // Debugging: Print the current steering angle to the Serial Monitor
    Serial.print("Absolute Angle: ");
    Serial.println(angle);
  }
}

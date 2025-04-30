#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

// Pins
const int HALL_PIN = 32;
const int SWITCH_PIN = 18;
const int LED_PIN = 19;

// WiFi Config
const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";
unsigned int localUdpPort = 7777;
WiFiUDP udp;

// UDP target
const char *udpAddress = "192.168.0.101";  // <-- Change this if needed
const unsigned int udpPort = 7777;

// State variables
bool lastSwitchState = HIGH;  // Using INPUT_PULLUP, HIGH = OFF
bool active = false;
float offset = 0.0;

void setup() {
  // Pins
  pinMode(HALL_PIN, INPUT_PULLUP);
  pinMode(SWITCH_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Serial
  Serial.begin(115200);

  // WiFi
  WiFi.hostname("Brake_ESP");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting with WiFi...");
  }
  Serial.println("Connected to WiFi.");
  udp.begin(localUdpPort);

  delay(1000);  // Let sensor settle
}

void loop() {
  bool currentSwitchState = digitalRead(SWITCH_PIN);

  // Detect switch going from OFF to ON
  if (lastSwitchState == HIGH && currentSwitchState == LOW) {
    active = true;
    digitalWrite(LED_PIN, HIGH); // LED ON
    int sensorValue = analogRead(HALL_PIN);
    offset = (1.0 - ((float)sensorValue / 4095.0)) * 360.0;
    Serial.print("Switch ON: Offset set to ");
    Serial.println(offset);
  }

  // Detect switch going from ON to OFF
  if (lastSwitchState == LOW && currentSwitchState == HIGH) {
    active = false;
    digitalWrite(LED_PIN, LOW); // LED OFF
    Serial.println("Switch OFF: Sensor reading paused");
  }

  lastSwitchState = currentSwitchState;

  if (active) {
    int sensorValue = analogRead(HALL_PIN);

    // Reversed direction: 0 = 360°, 4095 = 0°
    float angle = (1.0 - ((float)sensorValue / 4095.0)) * 360.0;

    // Apply offset (allow negative values)
    angle -= offset;

    // Optional: Only send if angle is positive
    if (angle < 0) {
      angle = 0.0;
    }

    // Print
    Serial.print("Sensor Value: ");
    Serial.print(sensorValue);
    Serial.print(" | Relative Angle: ");
    Serial.println(angle);

    // Prepare JSON
    StaticJsonDocument<200> doc;
    doc["sensor"] = "Brake";
    doc["angle"] = angle;
    String jsonStr;
    serializeJson(doc, jsonStr);

    // Send via UDP
    udp.beginPacket(udpAddress, udpPort);
    udp.print(jsonStr);
    udp.endPacket();
  }

  delay(50); // Sampling rate
}


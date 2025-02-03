#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

// WIFI
const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";
unsigned int localUdpPort = 7778;
WiFiUDP udp;

// SENSOR
const int SPEED_PIN = 32;
const int PEDAL_PIN = 33;
const int UDP_DELAY_MS = 20;
const int SPEED_MAGNETS = 5;
const int PEDAL_MAGNETS = 4;

// TODO: deal with integer overflows
struct rotationMetrics {
  uint64_t time_difference = 0;
  uint64_t time = 0;
};
rotationMetrics speed_metrics;
rotationMetrics pedal_metrics;

void IRAM_ATTR speed_isr() {
  int current_time = micros();
  speed_metrics.time_difference = current_time - speed_metrics.time;
  speed_metrics.time = current_time;
}

void IRAM_ATTR pedal_isr() {
  int current_time = micros();
  pedal_metrics.time_difference = current_time - pedal_metrics.time;
  pedal_metrics.time = current_time;
}

float calculate_speed(rotationMetrics metrics, int n_magnets) {
  uint64_t time = micros();
  uint64_t time_difference = 0;

  // reduce speed gradually if no more interrupts are occuring
  if (time - metrics.time > metrics.time_difference) {
    time_difference = time - metrics.time;
  }
  else {
    time_difference = metrics.time_difference;
  }

  float speed = 1000000.0 / (time_difference * n_magnets);

  if (speed < 0.01) {
    speed = 0;
  }

  return speed;
}

void setup() {
  // WIFI
  WiFi.hostname("Rotation_ESP");
  WiFi.begin(ssid, password);

  pinMode(SPEED_PIN, INPUT_PULLUP);
  attachInterrupt(SPEED_PIN, speed_isr, FALLING);

  pinMode(PEDAL_PIN, INPUT_PULLUP);
  attachInterrupt(PEDAL_PIN, pedal_isr, FALLING);

  Serial.begin(115200);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.println("Connecting with WiFi");
  }

  Serial.println("Connection with WiFi successful");
  udp.begin(localUdpPort);
}

void loop() {
  // Calculate speed
  float rotation_speed = calculate_speed(speed_metrics, SPEED_MAGNETS);
  float pedal_speed = calculate_speed(pedal_metrics, PEDAL_MAGNETS);
  
  // Build JSON message
  StaticJsonDocument<500> doc;
  String jsonStr;
  doc["sensor"] = "Rotation";
  doc["speed"] = rotation_speed;
  doc["pedal"] = pedal_speed;
  serializeJson(doc, jsonStr);

  // Read UDP messages
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char packetBuffer[255];
    udp.read(packetBuffer, packetSize);

    Serial.print("Received message: ");
    Serial.println(packetBuffer);
  }

  // Send UDP message
  udp.beginPacket("192.168.0.101", localUdpPort);
  udp.print(jsonStr);
  udp.endPacket();

  Serial.println(jsonStr);

  delay(UDP_DELAY_MS);
}
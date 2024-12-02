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
const int HALL_PIN = 32;
const int UDP_DELAY_MS = 20;
const int N_MAGNETS = 4;
const int AVG_SIZE = 50;  // Sliding average window size
const int AVG_DELAY = UDP_DELAY_MS * AVG_SIZE;

// TODO: deal with integer overflows
struct rotationMetrics {
  int count = 0;
  int counts[AVG_SIZE] = {0};
  float speed = 0;
  float acceleration = 0;
};
rotationMetrics metrics;

void IRAM_ATTR isr() {
  metrics.count++;
}

void setup() {
  // WIFI
  WiFi.hostname("Rotation_ESP");
  WiFi.begin(ssid, password);

  pinMode(HALL_PIN, INPUT_PULLUP);
  attachInterrupt(HALL_PIN, isr, FALLING);

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
  for (int k=AVG_SIZE-1; k>0; k--) {
    metrics.counts[k] = metrics.counts[k-1];
  }
  metrics.counts[0] = metrics.count;
  metrics.speed = (1000.0 * (metrics.counts[0] - metrics.counts[AVG_SIZE-1])) / float(AVG_DELAY * N_MAGNETS);
  
  // Build JSON message
  StaticJsonDocument<500> doc;
  String jsonStr;
  doc["sensor"] = "Rotation";
  doc["sensor_value"] = metrics.speed;
  doc["count"] = metrics.count;
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
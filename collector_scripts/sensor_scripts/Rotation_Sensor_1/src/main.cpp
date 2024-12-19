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
const int N_MAGNETS = 6;  // TODO: different amount of magnets for pedal and backwheel
const int AVG_SIZE = 50;  // Sliding average window size
const int AVG_DELAY = UDP_DELAY_MS * AVG_SIZE;

// TODO: deal with integer overflows
struct rotationMetrics {
  int count = 0;
  int counts[AVG_SIZE] = {0};
  float speed = 0;
  float acceleration = 0;
};
rotationMetrics speed_metrics;
rotationMetrics pedal_metrics;

void IRAM_ATTR speed_isr() {
  speed_metrics.count++;
}

void IRAM_ATTR pedal_isr() {
  pedal_metrics.count++;
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
  for (int k=AVG_SIZE-1; k>0; k--) {
    speed_metrics.counts[k] = speed_metrics.counts[k-1];
    pedal_metrics.counts[k] = pedal_metrics.counts[k-1];
  }
  speed_metrics.counts[0] = speed_metrics.count;
  pedal_metrics.counts[0] = pedal_metrics.count;
  speed_metrics.speed = (1000.0 * (speed_metrics.counts[0] - speed_metrics.counts[AVG_SIZE-1])) / float(AVG_DELAY * N_MAGNETS);
  pedal_metrics.speed = (1000.0 * (pedal_metrics.counts[0] - pedal_metrics.counts[AVG_SIZE-1])) / float(AVG_DELAY * N_MAGNETS);
  
  // Build JSON message
  StaticJsonDocument<500> doc;
  String jsonStr;
  doc["sensor"] = "Rotation";
  doc["speed"] = speed_metrics.speed;
  doc["pedal"] = pedal_metrics.speed;
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
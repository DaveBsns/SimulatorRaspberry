#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

// SENSOR
const int HALL_PIN = 32;

// WIFI
const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";
unsigned int localUdpPort = 7778;

WiFiUDP udp;

void setup() {
  // WIFI
  WiFi.hostname("Rotation_ESP");
  WiFi.begin(ssid, password);

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
  // put your main code here, to run repeatedly:
//   Serial.println("LED is on");
//   delay(1000);
//   Serial.println("LED is off");
//   delay(1000);

  StaticJsonDocument<500> doc;

  String jsonStr;
  doc["sensor"] = "Rotation";
  doc["sensor_value"] = 5;
  serializeJson(doc, jsonStr);

  // Read UDP messages
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char packetBuffer[255];
    udp.read(packetBuffer, packetSize);

    Serial.print("Received message: ");
    Serial.println(packetBuffer);
  }

  udp.beginPacket("192.168.0.101", localUdpPort);
  udp.print(jsonStr);
  udp.endPacket();

  Serial.println(jsonStr);

  delay(2000);
}
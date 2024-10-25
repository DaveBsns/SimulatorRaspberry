#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

// SENSOR
const int HALL_PIN = 32;

// WIFI
const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";
unsigned int localUdpPort = 7777;

// SWITCH
const int switchPin = 18;
const int ledPin = 19;
int switchState = 0;
int delayTime = 1000;


WiFiUDP udp;

void setup()
{

  // SWITCH
  pinMode(switchPin, INPUT_PULLUP);
  // Set the LED pin as output
  pinMode(ledPin, OUTPUT);
  // Turn off the LED initially
  digitalWrite(ledPin, LOW);


  // SENSOR
  pinMode(HALL_PIN, INPUT_PULLUP);
  delay(1000);


  // WIFI
  WiFi.hostname("Brake_ESP");

  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.println("Connecting with WiFi");
  }

  Serial.println("Connection with WiFi successful");
  udp.begin(localUdpPort);
}

void loop()
{

  int sensorValue = analogRead(HALL_PIN); // read Sensor value
  StaticJsonDocument<500> doc;

  String jsonStr;
  doc["sensor"] = "Brake";
  doc["sensor_value"] = sensorValue;
  Serial.print("Sensor Value: ");
  Serial.println(sensorValue);

  serializeJson(doc, jsonStr);

  // Read UDP messages
  int packetSize = udp.parsePacket();
  if (packetSize)
  {
    char packetBuffer[255];
    udp.read(packetBuffer, packetSize);

    Serial.print("Received message: ");
    Serial.println(packetBuffer);
  }





  if (switchState == 0) {
    if (sensorValue > 10) {
      udp.beginPacket("192.168.0.101", 7777);
      //udp.beginPacket("192.168.1.104", 7777);
      udp.print(jsonStr);
      udp.endPacket();
    }
  } else {
    udp.beginPacket("192.168.0.101", 7777);
    //udp.beginPacket("192.168.1.104", 7777);
    udp.print(jsonStr);
    udp.endPacket();
  }

  switchState = digitalRead(switchPin);

  // Control the LED based on the switch state
  if (switchState == LOW) {
    Serial.println("Switch is pressed - LED ON");
    digitalWrite(ledPin, HIGH);  // Turn the LED on
    delayTime = 50;
  } else {
    Serial.println("Switch is not pressed - LED OFF");
    digitalWrite(ledPin, LOW);   // Turn the LED off
    delayTime = 1000;
  }

  delay(delayTime);

}

/*#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

// WIFI
const char *ssid = "Arduino2"; //"Bicycle_Simulator_Network";
const char *password = "pommespanzer"; //"17701266";
unsigned int localUdpPort = 7777; // Must match the sending ESP32's port

WiFiUDP udp;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("WiFi connected.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Start UDP listener
  udp.begin(localUdpPort);
  Serial.println("UDP listener started.");
}

void loop() {
  // Check if a UDP packet has been received
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char packetBuffer[255]; // Buffer for incoming data
    int len = udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0; // Null-terminate the string
    }

    Serial.print("Received packet: ");
    Serial.println(packetBuffer);

    // Parse the incoming JSON data
    StaticJsonDocument<500> doc;
    DeserializationError error = deserializeJson(doc, packetBuffer);

    if (error) {
      Serial.print("Failed to parse JSON: ");
      Serial.println(error.c_str());
      return;
    }

    // Extract the sensor data
    const char* sensor = doc["sensor"];
    int sensorValue = doc["sensor_value"];

    Serial.print("Sensor: ");
    Serial.println(sensor);
    Serial.print("Sensor Value: ");
    Serial.println(sensorValue);
  }

  // Short delay to avoid overloading the serial output
  delay(100);
}*/



#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

// HALL EFFECT SENSOR
const int HALL_PIN = 32; // Pin connected to the brake sensor

// WIFI CONFIGURATION
const char *ssid = "Bicycle_Simulator_Network"; // WiFi network SSID
const char *password = "17701266";             // WiFi network password
unsigned int localUdpPort = 7777;              // UDP port for communication

// SWITCH AND LED CONFIGURATION
const int switchPin = 18;  // Pin connected to the control switch
const int ledPin = 19;     // Pin connected to the indicator LED
int switchState = 0;       // Current state of the switch
int delayTime = 1000;      // Delay time for the main loop

WiFiUDP udp; // UDP instance for communication

void setup()
{
  // SWITCH AND LED SETUP
  pinMode(switchPin, INPUT_PULLUP); // Configure switch pin as input with pull-up
  pinMode(ledPin, OUTPUT);          // Configure LED pin as output
  digitalWrite(ledPin, LOW);        // Turn off the LED initially

  // HALL EFFECT SENSOR SETUP
  pinMode(HALL_PIN, INPUT_PULLUP);  // Configure the hall effect sensor pin as input
  delay(1000);                      // Initial delay for stability

  // WIFI SETUP
  WiFi.hostname("Brake_ESP");       // Set the device hostname
  Serial.begin(115200);             // Initialize serial communication for debugging
  WiFi.begin(ssid, password);       // Begin WiFi connection

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);                    // Retry every second until connected
    Serial.println("Connecting with WiFi");
  }

  Serial.println("Connection with WiFi successful");
  udp.begin(localUdpPort);          // Initialize UDP communication
}

void loop()
{
  // READ HALL EFFECT SENSOR VALUE
  int sensorValue = analogRead(HALL_PIN); // Read the sensor value
  StaticJsonDocument<500> doc;           // Create a JSON document for data transmission
  String jsonStr;

  // Populate JSON with sensor data
  doc["sensor"] = "Brake";          // Identify this as the brake sensor
  doc["sensor_value"] = sensorValue; // Current brake sensor value
  Serial.print("Sensor Value: ");
  Serial.println(sensorValue);

  serializeJson(doc, jsonStr);      // Serialize JSON data into a string

  // READ INCOMING UDP MESSAGES
  int packetSize = udp.parsePacket();
  if (packetSize)
  {
    char packetBuffer[255];
    udp.read(packetBuffer, packetSize); // Read the incoming packet

    Serial.print("Received message: ");
    Serial.println(packetBuffer);      // Print the received message
  }

  // SEND SENSOR DATA BASED ON SWITCH STATE
  if (switchState == 0) {
    if (sensorValue > 10) {             // Send data if sensor value exceeds threshold
      udp.beginPacket("192.168.0.101", 7777); // Send to the main VR PC
      udp.print(jsonStr);
      udp.endPacket();
    }
  } else {
    udp.beginPacket("192.168.0.101", 7777); // Always send data when switch is active
    udp.print(jsonStr);
    udp.endPacket();
  }

  // UPDATE SWITCH STATE AND LED
  switchState = digitalRead(switchPin); // Read the current switch state

  if (switchState == LOW) {
    Serial.println("Switch is pressed - LED ON");
    digitalWrite(ledPin, HIGH);  // Turn the LED on when switch is pressed
    delayTime = 50;              // Shorten delay for faster response
  } else {
    Serial.println("Switch is not pressed - LED OFF");
    digitalWrite(ledPin, LOW);   // Turn the LED off when switch is not pressed
    delayTime = 1000;            // Lengthen delay for slower updates
  }

  delay(delayTime);              // Wait for the configured delay time
}

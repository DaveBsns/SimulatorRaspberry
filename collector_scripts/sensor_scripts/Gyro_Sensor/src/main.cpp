#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include "BNO055_support.h"

// WiFi and UDP config
const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";
const unsigned int localUdpPort = 8888;
const char *udpTargetIp = "192.168.0.101"; // Destination
const unsigned int udpTargetPort = 8888;

WiFiUDP udp;

struct bno055_t myBNO;
struct bno055_euler myEulerData;

float headingOffset = 0.0;
float rollOffset = 0.0;
float pitchOffset = 0.0;

void connectToWiFi() {
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");

    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
        delay(500);
        Serial.print(".");
        retries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected.");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
        udp.begin(localUdpPort);
    } else {
        Serial.println("\nFailed to connect to WiFi.");
    }
}

void setup() {
	delay(1000); // Give some time for the serial monitor to open
    Wire.begin();
    Serial.begin(115200);

    // Sensor init
    BNO_Init(&myBNO);
    bno055_set_operation_mode(OPERATION_MODE_NDOF);
    delay(100);

    bno055_read_euler_hrp(&myEulerData);
    headingOffset = myEulerData.h / 16.0;
    rollOffset = myEulerData.r / 16.0;
    pitchOffset = myEulerData.p / 16.0;

    Serial.println("Initial Offsets:");
    Serial.print("Heading: "); Serial.println(headingOffset);
    Serial.print("Roll: "); Serial.println(rollOffset);
    Serial.print("Pitch: "); Serial.println(pitchOffset);

    connectToWiFi();
}

void loop() {
    // Auto-reconnect WiFi if dropped
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected. Attempting reconnect...");
        connectToWiFi();
        delay(2000);
        return;
    }

    bno055_read_euler_hrp(&myEulerData);
    float relHeading = (myEulerData.h / 16.0) - headingOffset;
    float relRoll = (myEulerData.r / 16.0) - rollOffset;
    float relPitch = (myEulerData.p / 16.0) - pitchOffset;

    StaticJsonDocument<256> doc;
    doc["sensor"] = "BNO055";
    doc["euler_h"] = relHeading;
    doc["euler_r"] = relRoll;
    doc["euler_p"] = relPitch;

    String jsonStr;
    serializeJson(doc, jsonStr);

    int result = udp.beginPacket(udpTargetIp, udpTargetPort);
    if (result) {
        udp.print(jsonStr);
        udp.endPacket();
    } else {
        Serial.println("⚠️ Failed to start UDP packet.");
    }

    delay(10);
}